from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.chat import router
from typing import List
import time
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Cacticultures API Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dev.cacticultures.com",
        "https://staging.cacticultures.com",
        "https://cacticultures.com",
        "http://localhost:8001",  # Dev server
        "http://localhost:8002",  # Staging server
        "http://localhost:8003",  # Prod server
        "http://localhost:3000",  # Next.js dev server
        "http://localhost:8000"   # Local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    expose_headers=[
        "X-Process-Time",
        "X-API-Version",
    ],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Error Handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# General error handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)} - Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Middleware for processing time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Version"] = settings.API_V1_STR
    return response

# Include API router
app.include_router(router, prefix=settings.API_V1_STR)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint that returns detailed system status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "api_version": settings.API_V1_STR,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "cors": {
            "origins": app.state.cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        },
        "system": {
            "python_version": os.sys.version,
            "processors": os.cpu_count()
        }
    }

# Startup Event
@app.on_event("startup")
async def startup_event():
    """
    Initialize any connections or resources on startup
    """
    logger.info("Starting up FastAPI application")
    # Store CORS origins in app state for health check
    app.state.cors_origins = [
        "https://dev.cacticultures.com",
        "https://staging.cacticultures.com",
        "https://cacticultures.com",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    logger.info("FastAPI application startup complete")

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up any connections or resources on shutdown
    """
    logger.info("Shutting down FastAPI application")

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that returns basic API information
    """
    return {
        "app_name": settings.APP_NAME,
        "api_version": settings.API_V1_STR,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_check": "/health"
    }
