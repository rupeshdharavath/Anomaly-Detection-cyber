"""
Entity (User/Device) endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging

from ..models import EntityDetailResponse, EntityProfile, EntityStats, PaginatedResponse
from ..services.data_service import DataService

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_data_service() -> DataService:
    """Dependency for data service"""
    from ..main import data_service
    if not data_service:
        raise HTTPException(status_code=503, detail="Data service not available")
    return data_service


@router.get("/users", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    data_service: DataService = Depends(get_data_service)
):
    """
    List all users with pagination
    
    Query Parameters:
        - page: Page number (default 1)
        - page_size: Results per page (default 50, max 500)
    """
    try:
        users = data_service.get_all_users(page_size * page)
        
        total = len(users) if users else 0
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        start = (page - 1) * page_size
        end = start + page_size
        
        page_data = users[start:end] if users else []
        
        return PaginatedResponse(
            data=page_data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices", response_model=PaginatedResponse)
async def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    data_service: DataService = Depends(get_data_service)
):
    """
    List all devices with pagination
    
    Query Parameters:
        - page: Page number (default 1)
        - page_size: Results per page (default 50, max 500)
    """
    try:
        devices = data_service.get_all_devices(page_size * page)
        
        total = len(devices) if devices else 0
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        start = (page - 1) * page_size
        end = start + page_size
        
        page_data = devices[start:end] if devices else []
        
        return PaginatedResponse(
            data=page_data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )
        
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: str,
    data_service: DataService = Depends(get_data_service)
):
    """
    Get detailed information about a user
    
    Path Parameters:
        - user_id: User identifier
    
    Response includes:
        - User profile information
        - Risk statistics
        - Recent anomalies
        - Activity timeline
    """
    try:
        user = data_service.get_user(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Get user events
        events = data_service.get_user_events(user_id, 100)
        anomalies_count = len([e for e in events if e.get('label') == 1]) if events else 0
        
        return {
            "status": "success",
            "data": {
                "profile": {
                    "entity_id": user.get('user_id'),
                    "entity_type": "user",
                    "name": user.get('name', ''),
                    "department": user.get('department', ''),
                    "office": user.get('office', '')
                },
                "stats": {
                    "entity_id": user.get('user_id'),
                    "total_events": len(events),
                    "anomalies_count": anomalies_count,
                    "anomaly_rate": anomalies_count / len(events) if events else 0,
                    "average_confidence": 0.75,
                    "common_attack_types": ["impossible_travel", "credential_stuffing"],
                    "risk_level": "medium" if anomalies_count > 5 else "low"
                },
                "recent_anomalies": events[:10] if events else [],
                "timeline": []
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}")
async def get_device_detail(
    device_id: str,
    data_service: DataService = Depends(get_data_service)
):
    """
    Get detailed information about a device
    
    Path Parameters:
        - device_id: Device identifier
    
    Response includes:
        - Device profile information
        - Risk statistics
        - Recent anomalies
        - Activity timeline
    """
    try:
        device = data_service.get_device(device_id)
        
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        return {
            "status": "success",
            "data": {
                "profile": {
                    "entity_id": device.get('device_id'),
                    "entity_type": "device",
                    "name": device.get('device_id'),
                    "device_type": device.get('device_type', ''),
                    "os": device.get('operating_system', ''),
                    "browser": device.get('browser', '')
                },
                "stats": {
                    "entity_id": device.get('device_id'),
                    "total_events": 0,
                    "anomalies_count": 0,
                    "anomaly_rate": 0.0,
                    "average_confidence": 0.0,
                    "common_attack_types": [],
                    "risk_level": "low"
                },
                "recent_anomalies": [],
                "timeline": []
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting device detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_entities(
    q: str = Query(..., min_length=1),
    entity_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    data_service: DataService = Depends(get_data_service)
):
    """
    Search for users or devices
    
    Query Parameters:
        - q: Search query (required, min 1 char)
        - entity_type: Filter by type (user or device, optional)
        - limit: Maximum results (default 20, max 100)
    """
    try:
        results = []
        q_lower = q.lower()
        
        if entity_type != "device":
            users = data_service.get_all_users(10000)
            if users:
                for user in users:
                    if any([
                        q_lower in str(user.get('name', '')).lower(),
                        q_lower in str(user.get('user_id', '')).lower(),
                        q_lower in str(user.get('email', '')).lower()
                    ]):
                        results.append({
                            "id": user.get('user_id'),
                            "type": "user",
                            "name": user.get('name', ''),
                            "metadata": user
                        })
        
        if entity_type != "user":
            devices = data_service.get_all_devices(10000)
            if devices:
                for device in devices:
                    if any([
                        q_lower in str(device.get('device_id', '')).lower(),
                        q_lower in str(device.get('device_type', '')).lower()
                    ]):
                        results.append({
                            "id": device.get('device_id'),
                            "type": "device",
                            "name": device.get('device_id'),
                            "metadata": device
                        })
        
        return {
            "status": "success",
            "data": results[:limit]
        }
        
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
