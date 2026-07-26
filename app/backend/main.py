"""
FastAPI Main Application
Anomaly Detection System Backend
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional

from .config import settings
from .services.inference_service import InferenceService
from .services.alert_service import AlertService
from .services.data_service import DataService
from .routers import (
    anomalies,
    alerts,
    analytics,
    entities,
    health,
    models
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services (loaded on startup)
inference_service: Optional[InferenceService] = None
alert_service: Optional[AlertService] = None
data_service: Optional[DataService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Anomaly Detection Backend...")
    global inference_service, alert_service, data_service
    
    try:
        # Initialize data service first (loads CSV artifacts)
        data_service = DataService()
        # Then load inference service and models
        inference_service = InferenceService()
        # Finally initialize alert service with data access
        alert_service = AlertService(data_service)
        alert_service.seed_initial_alerts()
        logger.info("✅ Services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Anomaly Detection Backend...")


# Create FastAPI app
app = FastAPI(
    title="Anomaly Detection System API",
    description="Cybersecurity Anomaly Detection with LSTM and Baseline Profiling",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(anomalies.router, prefix="/api/v1/anomalies", tags=["Anomalies"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["Entities"])
app.include_router(models.router, prefix="/api/v1/models", tags=["Models"])


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Anomaly Detection System",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "anomalies": "/api/v1/anomalies",
            "alerts": "/api/v1/alerts",
            "analytics": "/api/v1/analytics",
            "entities": "/api/v1/entities",
            "models": "/api/v1/models"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
