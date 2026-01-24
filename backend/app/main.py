from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api import auth, search, compare, stream, admin, metadata, preferences
from app.db import init_db
from app.middleware.error_handler import ErrorHandlerMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    yield


app = FastAPI(
    title="Holly Search API",
    description="Sacred Texts RAG Search API - Kuran, Incil, Tevrat",
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
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.app_env,
    }


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
