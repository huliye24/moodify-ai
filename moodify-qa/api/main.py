"""Moodify QA API - FastAPI application.

Main entry point for the Moodify QA API service.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.routes.qa import router as qa_router
from api.schemas.report import HealthResponse, VersionResponse

# Application metadata
APP_VERSION = "0.2.0"
API_VERSION = "v1"
START_TIME = datetime.utcnow()

# Create FastAPI app
app = FastAPI(
    title="Moodify QA API",
    description="""
    **Moodify QA** - AI Audio Quality Assurance Infrastructure

    ## Overview

    Moodify QA provides professional-grade audio quality analysis via REST API.

    ## Key Features

    * **Single File Analysis**: Upload and analyze individual audio files
    * **Batch Processing**: Analyze multiple files simultaneously
    * **Quality Scoring**: 0-100 QA score with detailed breakdown
    * **Issue Detection**: Automatic detection of audio quality issues
    * **Recommendations**: Actionable improvement suggestions
    * **Webhook Support**: Receive notifications when analysis completes

    ## Target Users

    * AI Music Platforms
    * Music Companies
    * Copyright Owners
    * Audio Production Studios

    ## Authentication

    Currently no authentication required (development mode).
    Production deployments should implement API key authentication.

    ## Rate Limits

    * Single file: 100MB max
    * Batch: 50 files max, 500MB total
    * Rate: 100 requests/minute per IP

    ## Supported Formats

    * WAV
    * MP3
    * FLAC
    * AIFF
    * OGG
    * M4A
    """,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(qa_router, prefix="/api/v1")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint - API info."""
    return {
        "name": "Moodify QA API",
        "version": APP_VERSION,
        "api_version": API_VERSION,
        "documentation": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service health status and basic statistics.
    """
    uptime = (datetime.utcnow() - START_TIME).total_seconds()

    # Get queue size from storage
    try:
        from api.storage.database import TaskStorage
        storage = TaskStorage()
        stats = storage.get_stats()
        queue_size = stats.get("status_counts", {}).get("pending", 0)
    except Exception:
        queue_size = 0

    return HealthResponse(
        status="healthy",
        version=APP_VERSION,
        uptime_seconds=int(uptime),
        queue_size=queue_size,
    )


@app.get("/version", response_model=VersionResponse)
async def version():
    """
    API version information.

    Returns current API and service versions.
    """
    return VersionResponse(
        api_version=API_VERSION,
        service_version=APP_VERSION,
        build_date=START_TIME.isoformat(),
    )


@app.get("/api/v1/version", response_model=VersionResponse)
async def version_v1():
    """Version endpoint under API v1 prefix."""
    return await version()


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup."""
    print(f"Moodify QA API v{APP_VERSION} starting...")
    print(f"Documentation: http://localhost:8000/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    print("Moodify QA API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
