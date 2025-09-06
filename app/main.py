"""FastAPI application main module."""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.db import close_mongo_connection, connect_to_mongo, ensure_indexes
from app.deps import limiter, rate_limit_exceeded_handler
from app.middleware.errors import setup_error_handlers
from app.middleware.security_headers import setup_security_headers
from app.routes.auth_routes import router as auth_router
from app.utils.responses import ok


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting Clinic Auth API...")
    logger.info(f"📋 Environment: {settings.app_name}")
    logger.info(f"🔧 Port: {settings.port}")
    logger.info(f"🐛 Debug: {settings.debug}")
    
    # Connect to database
    await connect_to_mongo()
    await ensure_indexes()
    logger.info("✅ Database connected and indexes created")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Clinic Auth API...")
    await close_mongo_connection()
    logger.info("✅ Database connection closed")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Production-ready FastAPI authentication API with JWT tokens and MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Setup middleware
setup_security_headers(app)
setup_error_handlers(app)

# Include routers
app.include_router(auth_router)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return ok(data={
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.app_name,
        "version": "1.0.0"
    })


@app.head("/health", tags=["System"])
async def health_check_head():
    """Health check endpoint (HEAD method)."""
    return None


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
