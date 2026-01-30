"""
Main FastAPI application with enhanced features
"""
import os

import os

for k in [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy",
    "ALL_PROXY",
    "all_proxy"
]:
    os.environ.pop(k, None)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uvicorn

from api.routes import router
from config.settings import settings
from utils.logger import logger
from db.database import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Create necessary directories
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    logger.info("✅ Directories created")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application")
    await close_db()
    logger.info("✅ Cleanup completed")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced PDF RAG API with vector search and LLM integration",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Log request
    logger.info(f"📨 {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(f"✅ {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
    
    # Add custom headers
    response.headers["X-Process-Time"] = str(duration)
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
            "path": str(request.url.path)
        }
    )

# Include API router
app.include_router(router)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
