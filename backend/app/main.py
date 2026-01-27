from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging

from app.config import settings
from app.api import auth, search, compare, stream, admin, metadata, preferences
from app.db import init_db
from app.middleware.error_handler import ErrorHandlerMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")

    # Initialize Sentry if enabled
    if settings.sentry_enabled and settings.sentry_dsn_backend:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        def before_send(event, hint):
            """Redact sensitive query text from Sentry events"""
            if "request" in event:
                # Redact JSON body query fields
                if "data" in event["request"]:
                    data = event["request"]["data"]
                    if isinstance(data, dict):
                        # Redact common query field names
                        for key in ["query", "q", "search_query", "text"]:
                            if key in data:
                                data[key] = "[REDACTED]"
                    # Don't attempt to parse string bodies - too risky

                # Redact query parameters
                if "query_string" in event["request"]:
                    event["request"]["query_string"] = "[QUERY_PARAMS_REDACTED]"

            return event

        sentry_sdk.init(
            dsn=settings.sentry_dsn_backend,
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
            traces_sample_rate=settings.sentry_traces_sample_rate,
            environment=settings.sentry_environment,
            release="clarus-backend@2.0.0",
            send_default_pii=False,
            before_send=before_send,
        )
        logger.info(f"Sentry initialized for {settings.sentry_environment}")

    yield  # <-- App runs here

    # SHUTDOWN (triggered by uvicorn on SIGTERM/SIGINT)
    logger.info("Shutting down, cleaning up...")

    # Close database connections with timeout and error handling
    from app.db import engine

    try:
        await asyncio.wait_for(engine.dispose(), timeout=5.0)
        logger.info("Database connections closed")
    except asyncio.TimeoutError:
        logger.warning("Database disposal timed out after 5s, proceeding with shutdown")
    except Exception as e:
        logger.error(f"Error disposing database engine: {e}")

    # Cancel any pending tasks (best effort)
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()

    # Wait for task cancellation with timeout
    if tasks:
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True), timeout=5.0
            )
        except asyncio.TimeoutError:
            logger.warning(f"{len(tasks)} tasks did not cancel within timeout")

    logger.info("Shutdown complete")


app = FastAPI(
    title="Clarus API",
    description="Clarus RAG Search API - Kuran, Incil, Tevrat",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(ErrorHandlerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "X-Request-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ],
)


@app.middleware("http")
async def add_user_id_to_state(request: Request, call_next):
    from app.auth import decode_access_token

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = decode_access_token(token)
        if payload:
            user_id_str = payload.get("sub")
            if user_id_str:
                request.state.user_id = int(user_id_str)

    response = await call_next(request)
    return response


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(compare.router, prefix="/api/compare", tags=["compare"])
app.include_router(stream.router, prefix="/api/stream", tags=["stream"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(metadata.router, prefix="/api/metadata", tags=["metadata"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])


@app.get("/api/health")
async def health_check():
    status = "healthy"
    qdrant_status = "connected"
    event_loop_status = "ok"

    # Test event loop responsiveness (detects blocking)
    try:
        await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
    except asyncio.TimeoutError:
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

    return JSONResponse(
        status_code=200 if status == "healthy" else 503,
        content={
            "status": status,
            "version": "2.0.0",
            "event_loop": event_loop_status,
            "qdrant": qdrant_status,
        },
    )


@app.get("/api/config")
async def get_public_config():
    return {
        "success": True,
        "data": {
            "rate_limit_per_day": settings.rate_limit_per_day,
            "query_max_length": settings.query_max_length,
            "google_oauth_enabled": bool(settings.google_client_id),
        },
    }
