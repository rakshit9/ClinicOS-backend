"""FastAPI application main module."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.db import close_db, init_db
from app.deps import limiter
from app.middleware.errors import setup_error_handlers
from app.middleware.security_headers import setup_security_headers
from app.routes.auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting Clinic Auth API...")
    logger.info(f"📋 Environment: {settings.app_name}")
    logger.info(f"🔧 Port: {settings.port}")
    logger.info(f"🐛 Debug: {settings.debug}")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Clinic Auth API...")
    await close_db()
    logger.info("✅ Database connection closed")


# Create FastAPI app
app = FastAPI(
    title="Clinic Auth API",
    description="Production-ready authentication API for clinic management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
setup_security_headers(app)

# Setup error handlers
setup_error_handlers(app)

# Setup rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(auth_router)


@app.head("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/health")
async def health_check_detailed():
    """Detailed health check endpoint."""
    from app.utils.responses import ok
    
    return ok({
        "status": "healthy",
        "timestamp": "2025-09-06T00:00:00Z",
        "environment": settings.app_name,
        "version": "1.0.0"
    }, "Service is healthy")
