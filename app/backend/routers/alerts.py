"""
Alert management endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging
from datetime import datetime

from ..models import AlertResponse, AlertUpdate, PaginatedResponse
from ..services.alert_service import AlertService

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory alert store (would use database in production)
alerts_store = []


async def get_alert_service() -> AlertService:
    """Dependency for alert service"""
    from ..main import alert_service
    if not alert_service:
        raise HTTPException(status_code=503, detail="Alert service not available")
    return alert_service


@router.get("/", response_model=PaginatedResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    acknowledged: Optional[bool] = None,
    severity: Optional[str] = None,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    List alerts with pagination
    
    Query Parameters:
        - page: Page number (default 1)
        - page_size: Results per page (default 50, max 500)
        - acknowledged: Filter by acknowledgment status
        - severity: Filter by severity (info, warning, critical)
    """
    try:
        all_alerts = alert_service.get_all_alerts(1000)
        
        # Apply filters
        filtered = all_alerts
        
        if acknowledged is not None:
            filtered = [a for a in filtered if a.get('acknowledged') == acknowledged]
        
        if severity:
            filtered = [a for a in filtered if a.get('severity') == severity]
        
        # Pagination
        total = len(filtered)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        
        page_data = filtered[start:end]
        
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
        logger.error(f"Error listing alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active", response_model=PaginatedResponse)
async def get_active_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Get active (unacknowledged) alerts
    
    Query Parameters:
        - page: Page number (default 1)
        - page_size: Results per page (default 50, max 500)
    """
    try:
        active = alert_service.get_active_alerts(page_size * page)
        
        # Pagination
        total = len(active)
        total_pages = (total + page_size - 1) // page_size
        start = (page - 1) * page_size
        end = start + page_size
        
        page_data = active[start:end]
        
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
        logger.error(f"Error getting active alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Get specific alert by ID
    
    Path Parameters:
        - alert_id: Alert identifier
    """
    try:
        all_alerts = alert_service.get_all_alerts(10000)
        
        for alert in all_alerts:
            if alert.get('alert_id') == alert_id:
                return AlertResponse(
                    alert_id=alert.get('alert_id'),
                    anomaly_id=alert.get('anomaly_id'),
                    entity_id=alert.get('entity_id', 'unknown'),
                    risk_score=alert.get('risk_score', 0.0),
                    attack_type=alert.get('attack_type'),
                    confidence=alert.get('confidence', 0.0),
                    flagged_by=alert.get('flagged_by', 'none'),
                    severity=alert.get('severity'),
                    message=alert.get('message'),
                    action_required=alert.get('action_required', False),
                    created_at=datetime.fromisoformat(alert.get('created_at', datetime.now().isoformat())),
                    acknowledged=alert.get('acknowledged', False),
                    acknowledged_by=alert.get('acknowledged_by'),
                    acknowledged_at=datetime.fromisoformat(alert['acknowledged_at']) if alert.get('acknowledged_at') else None
                )
        
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    update: AlertUpdate,
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Acknowledge an alert
    
    Path Parameters:
        - alert_id: Alert identifier
    
    Request Body:
        - acknowledged: Boolean flag
        - acknowledged_by: User who acknowledged (optional)
    """
    try:
        if update.acknowledged:
            alert = alert_service.acknowledge_alert(alert_id, update.acknowledged_by or "system")
            if alert:
                return {
                    "status": "success",
                    "message": f"Alert {alert_id} acknowledged",
                    "alert": alert
                }
        
        raise HTTPException(status_code=404, detail=f"Could not update alert {alert_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_alert_statistics(
    alert_service: AlertService = Depends(get_alert_service)
):
    """Get alert statistics and summary"""
    try:
        stats = alert_service.get_alert_statistics()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting alert statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
