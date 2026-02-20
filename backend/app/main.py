import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api import (
    admin,
    auth,
    bible_keyword_search,
    compare,
    enhance,
    etymology,
    keyword_search,
    metadata,
    preferences,
    search,
    stream,
    verse_lookup,
    verse_translations,
    verse_words,
)
from app.config import settings
from app.db import init_db
from app.logging_config import LoggingConfig, get_logger, setup_logging
from app.middleware.correlation import CorrelationIDMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware, log_hsts_startup_warning
from app.schemas.sse_events import (
    CompareParagraphEvent,
    CompareProgressEvent,
    CompareStatsEvent,
    CompareVerseDetailsEvent,
    SearchCitationsEvent,
    SearchCompleteEvent,
    SearchStatusEvent,
    SearchTokenEvent,
    SearchVerseDetailsEvent,
    SSECompleteEvent,
    SSEErrorEvent,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    # Initialize structured logging first
    setup_logging(LoggingConfig.from_settings(settings))
    logger.info(
        "Structured logging initialized",
        extra={"log_level": settings.log_level, "log_format": settings.log_format},
    )

    # Validate production settings
    settings.validate_production_settings()
    log_hsts_startup_warning()

    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")

    logger.info("Connecting to Redis...")
    from app.redis_client import redis_manager

    await redis_manager.connect()
    if redis_manager.client:
        logger.info("Redis connected")
    else:
        logger.warning("Redis unavailable - caching disabled")

    # Initialize Sentry if enabled
    if settings.sentry_enabled and settings.sentry_dsn_backend:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        def before_send(event, hint):
            """Redact sensitive data from Sentry events - PII and LLM content"""

            # Define keys to scrub
            pii_keys = {"user_email", "user_name", "email", "name", "user_id"}
            llm_keys = {"llm_response", "content", "response", "answer", "completion"}

            def scrub_dict(d, keys_to_scrub):
                """Recursively scrub specified keys in a dictionary"""
                if not isinstance(d, dict):
                    return
                for key in keys_to_scrub:
                    if key in d:
                        d[key] = "[REDACTED]"

            # Scrub spans data (performance monitoring)
            if "spans" in event:
                for span in event.get("spans", []):
                    if isinstance(span, dict) and "data" in span:
                        scrub_dict(span["data"], pii_keys | llm_keys)

            # Scrub breadcrumbs data
            if "breadcrumbs" in event:
                breadcrumbs = event.get("breadcrumbs", {})
                if isinstance(breadcrumbs, dict):
                    for breadcrumb in breadcrumbs.get("values", []):
                        if isinstance(breadcrumb, dict) and "data" in breadcrumb:
                            scrub_dict(breadcrumb["data"], pii_keys | llm_keys)

            # Scrub request data (preserve query text for debugging)
            if "request" in event:
                # Redact JSON body query fields
                if "data" in event["request"]:
                    data = event["request"]["data"]
                    if isinstance(data, dict):
                        # Redact PII and LLM response fields
                        scrub_dict(data, pii_keys | llm_keys)
                    # Don't attempt to parse string bodies - too risky

                # Redact query parameters
                if "query_string" in event["request"]:
                    event["request"]["query_string"] = "[QUERY_PARAMS_REDACTED]"

            return event

        try:
            sentry_sdk.init(
                dsn=settings.sentry_dsn_backend,
                integrations=[
                    StarletteIntegration(transaction_style="endpoint"),
                    FastApiIntegration(transaction_style="endpoint"),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=settings.sentry_traces_sample_rate,
                environment=settings.sentry_environment,
                release="clarus-backend@2.0.0",
                send_default_pii=False,
                before_send=before_send,
                auto_enabling_integrations=False,
            )
            logger.info(
                "Sentry initialized",
                extra={
                    "environment": settings.sentry_environment,
                    "traces_sample_rate": settings.sentry_traces_sample_rate,
                },
            )
        except Exception as e:
            logger.error(
                "Sentry initialization failed; continuing without Sentry",
                extra={"error_type": type(e).__name__},
                exc_info=True,
            )

    yield  # <-- App runs here

    # SHUTDOWN (triggered by uvicorn on SIGTERM/SIGINT)
    logger.info("Shutdown initiated", extra={"reason": "lifespan_end"})

    try:
        from app.redis_client import redis_manager as _redis_manager

        await _redis_manager.disconnect()
        logger.info("Redis disconnected")
    except Exception as e:
        logger.warning("Error disconnecting Redis", extra={"error_type": type(e).__name__})

    # Close database connections with timeout and error handling
    from app.db import engine

    try:
        await asyncio.wait_for(engine.dispose(), timeout=5.0)
        logger.info("Database connections closed")
    except TimeoutError:
        logger.warning("Database disposal timed out", extra={"timeout_seconds": 5})
    except Exception as e:
        logger.error(
            "Error disposing database engine",
            extra={"error_type": type(e).__name__},
            exc_info=True,
        )

    # Cancel any pending tasks (best effort)
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    # Wait for task cancellation with timeout
    if tasks:
        try:
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=5.0)
        except TimeoutError:
            logger.warning(
                "Tasks did not cancel within timeout",
                extra={"pending_tasks": len(tasks), "timeout_seconds": 5},
            )

    logger.info("Shutdown complete")


app = FastAPI(
    title="Clarus API",
    description="Clarus RAG Search API - Kuran, Incil, Tevrat",
    version="2.0.0",
    lifespan=lifespan,
    # Disable API documentation in production to prevent attack surface exposure (#241)
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

if not settings.is_production:
    logger.info(
        "API documentation enabled",
        extra={"docs_url": "/docs", "redoc_url": "/redoc", "openapi_url": "/openapi.json"},
    )
else:
    logger.info("API documentation disabled in production (APP_ENV=production)")


def custom_openapi():
    """Inject security scheme definitions into the OpenAPI spec."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Add security schemes
    schema.setdefault("components", {})["securitySchemes"] = {
        "SessionCookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "better-auth.session_token",
            "description": "Better Auth session cookie (set automatically by browser after login)",
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for CLI access (generate via POST /api/auth/api-key)",
        },
    }

    sse_models: list[type[BaseModel]] = [
        SearchStatusEvent,
        SearchTokenEvent,
        SearchCitationsEvent,
        SearchVerseDetailsEvent,
        SearchCompleteEvent,
        CompareProgressEvent,
        CompareVerseDetailsEvent,
        CompareParagraphEvent,
        CompareStatsEvent,
        SSECompleteEvent,
        SSEErrorEvent,
    ]
    for model in sse_models:
        model_schema = model.model_json_schema(ref_template="#/components/schemas/{model}")
        defs = model_schema.pop("$defs", {})
        schema["components"]["schemas"][model.__name__] = model_schema
        for def_name, def_schema in defs.items():
            if def_name not in schema["components"]["schemas"]:
                schema["components"]["schemas"][def_name] = def_schema

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi  # type: ignore[method-assign]

# Middleware order: Last added = first executed
# Execution order: CorrelationIDMiddleware -> ErrorHandlerMiddleware -> SecurityHeadersMiddleware -> CORSMiddleware -> route
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-API-Key",
        "X-Request-ID",
        "X-Correlation-ID",
    ],
    expose_headers=[
        "X-Request-ID",
        "X-Correlation-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ],
)


@app.middleware("http")
async def csrf_protection(request: Request, call_next):
    """
    Basic CSRF protection: verify Origin header for state-changing requests.

    Validates Origin against allowed CORS origins for POST/PUT/DELETE/PATCH requests.
    Better Auth handles its own CSRF for /api/auth/* routes.
    """
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        origin = request.headers.get("origin")
        # Only validate if Origin header is present (browser requests)
        if origin:
            # Normalize origin (remove trailing slash)
            origin = origin.rstrip("/")
            allowed_origins = [o.rstrip("/") for o in settings.cors_origins_list]

            # Allow wildcard or check against whitelist
            if "*" not in allowed_origins and origin not in allowed_origins:
                logger.warning(
                    "CSRF validation failed",
                    extra={
                        "origin": origin,
                        "allowed_origins": allowed_origins,
                        "path": request.url.path,
                    },
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "success": False,
                        "error": {
                            "code": "CSRF_VALIDATION_FAILED",
                            "message": "Origin not allowed",
                            "details": [],
                        },
                    },
                )
    return await call_next(request)


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(enhance.router, prefix="/api/search", tags=["search"])
app.include_router(etymology.router, prefix="/api/etymology", tags=["etymology"])
app.include_router(compare.router, prefix="/api/compare", tags=["compare"])
app.include_router(stream.router, prefix="/api/stream", tags=["stream"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(metadata.router, prefix="/api/metadata", tags=["metadata"])
app.include_router(verse_translations.router, prefix="/api/metadata", tags=["metadata"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])
app.include_router(keyword_search.router, prefix="/api/search/keyword", tags=["keyword"])
app.include_router(
    bible_keyword_search.router,
    prefix="/api/keyword-search/bible",
    tags=["bible-keyword"],
)
app.include_router(verse_lookup.router, prefix="/api/verse", tags=["verse"])
app.include_router(verse_words.router, prefix="/api/quran/verses", tags=["verse-words"])


class RedisStatusInfo(BaseModel):
    status: str
    used_memory: str | None = None
    connected_clients: int | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    event_loop: str
    qdrant: str
    redis: RedisStatusInfo


class PublicConfigData(BaseModel):
    rate_limit_per_day: int
    query_max_length: int
    google_oauth_enabled: bool


class PublicConfigResponse(BaseModel):
    success: bool = True
    data: PublicConfigData


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    status = "healthy"
    qdrant_status = "connected"
    event_loop_status = "ok"
    redis_status = "disconnected"
    redis_memory = None
    redis_clients = None

    # Test event loop responsiveness (detects blocking)
    try:
        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
    except TimeoutError:
        status = "unhealthy"
        event_loop_status = "blocked"

    # Test Qdrant connectivity with 2s timeout
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(host="localhost", port=6333, timeout=2)
        await asyncio.wait_for(asyncio.to_thread(client.get_collections), timeout=2.0)
    except Exception:
        if status == "healthy":
            status = "degraded"
        qdrant_status = "disconnected"

    # Test Redis connectivity with 2s timeout
    try:
        from app.redis_client import redis_manager

        is_healthy = await asyncio.wait_for(redis_manager.health_check(), timeout=2.0)
        if is_healthy and redis_manager.client:
            redis_status = "connected"
            # Get Redis memory and client info
            try:
                info = await redis_manager.client.info(section="memory")
                redis_memory = info.get("used_memory_human", "unknown")
                if isinstance(redis_memory, bytes):
                    redis_memory = redis_memory.decode()
                clients_info = await redis_manager.client.info(section="clients")
                redis_clients = clients_info.get("connected_clients", 0)
            except Exception:
                pass  # Memory info is optional
        else:
            if status == "healthy":
                status = "degraded"
    except Exception:
        if status == "healthy":
            status = "degraded"

    return JSONResponse(
        status_code=200 if status != "unhealthy" else 503,
        content={
            "status": status,
            "version": "2.0.0",
            "event_loop": event_loop_status,
            "qdrant": qdrant_status,
            "redis": {
                "status": redis_status,
                "used_memory": redis_memory,
                "connected_clients": redis_clients,
            },
        },
    )


@app.get("/api/config", response_model=PublicConfigResponse)
async def get_public_config():
    return PublicConfigResponse(
        data=PublicConfigData(
            rate_limit_per_day=settings.rate_limit_per_day,
            query_max_length=settings.query_max_length,
            google_oauth_enabled=bool(settings.google_client_id),
        )
    )
