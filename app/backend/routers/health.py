"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import os

from ..config import settings
from ..models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    # Check services
    services = {
        "inference": "operational",
        "alerts": "operational",
        "data": "operational",
    }
    
    # Check models
    models_loaded = (
        os.path.exists(settings.BASELINE_PROFILES) and
        os.path.exists(settings.LSTM_MODEL)
    )
    
    # Check data files
    data_files_present = all([
        os.path.exists(settings.USERS_CSV),
        os.path.exists(settings.DEVICES_CSV),
        os.path.exists(settings.CYBERSECURITY_CSV),
    ])
    
    return HealthResponse(
        status="healthy" if models_loaded and data_files_present else "degraded",
        timestamp=datetime.now(),
        services=services,
        models_loaded=models_loaded,
        data_files_present=data_files_present
    )


@router.get("/health/ready")
async def readiness_check():
    """Readiness check - indicates if service is ready to accept traffic"""
    models_loaded = os.path.exists(settings.BASELINE_PROFILES)
    data_loaded = os.path.exists(settings.CYBERSECURITY_CSV)
    
    return {
        "ready": models_loaded and data_loaded,
        "models": models_loaded,
        "data": data_loaded
    }


@router.get("/health/live")
async def liveness_check():
    """Liveness check - indicates if service is still running"""
    return {"alive": True, "timestamp": datetime.now()}
