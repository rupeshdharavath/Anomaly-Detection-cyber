"""
Anomaly detection endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import Optional
import logging

from ..models import (
    InferenceRequest,
    InferenceResponse,
    BatchInferenceRequest,
    BatchInferenceResponse,
    AnomalyFilter,
    AnomalyResponse,
    PaginatedResponse
)
from ..services.inference_service import InferenceService

router = APIRouter()
logger = logging.getLogger(__name__)

# Store for results (would use database in production)
anomaly_store = []
anomaly_counter = 0


async def get_inference_service() -> InferenceService:
    """Dependency for inference service"""
    from ..main import inference_service
    if not inference_service:
        raise HTTPException(status_code=503, detail="Inference service not available")
    return inference_service


@router.post("/detect", response_model=InferenceResponse)
async def detect_anomaly(
    request: InferenceRequest,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Detect anomaly for a single event
    
    Request:
        - event_id: Unique event identifier
        - timestamp: Event timestamp
        - entity_id: User or device ID
        - resource_accessed: Resource being accessed
        - geo_location: Geographic location
        - auth_method: Authentication method used
        - device_type: Device type
        - failed_login_attempts: Number of failed logins
        - session_duration: Session duration in seconds
    
    Response:
        - is_anomaly: Whether event is anomalous
        - confidence: Confidence score (0-1)
        - risk_score: Overall risk score
        - risk_level: Risk level (low, medium, high, critical)
        - flagged_by: Which model flagged it (baseline, lstm, or both)
        - reasons: List of reasons for the detection
        - suggested_action: Suggested action to take
    """
    try:
        # Convert request to dict
        event_data = request.model_dump()
        
        # Run inference
        result = inference_service.predict(event_data)
        
        # Store result
        global anomaly_counter
        anomaly_counter += 1
        result['anomaly_id'] = f"ANO-{anomaly_counter}"
        anomaly_store.append(result)
        
        # Convert to response model
        return InferenceResponse(
            event_id=result.get('event_id'),
            is_anomaly=bool(result.get('is_anomaly', False)),
            confidence=float(result.get('confidence', 0.0)),
            risk_score=float(result.get('risk_score', 0.0)),
            risk_level=result.get('risk_level', 'low'),
            baseline_score=float(result.get('baseline_score', 0.0)),
            lstm_confidence=float(result.get('lstm_confidence', 0.0)),
            flagged_by=result.get('flagged_by', 'none'),
            attack_type=result.get('attack_type') or 'unknown',
            reasons=result.get('reasons', []),
            suggested_action=result.get('suggested_action', 'Monitor')
        )
        
    except Exception as e:
        logger.error(f"Error in anomaly detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect/batch", response_model=BatchInferenceResponse)
async def detect_batch_anomalies(
    request: BatchInferenceRequest,
    inference_service: InferenceService = Depends(get_inference_service)
):
    """
    Detect anomalies for multiple events in batch
    
    Request:
        - events: List of events to process
    
    Response:
        - results: List of inference results
        - processing_time: Time taken to process batch
        - total_anomalies: Number of anomalies detected
    """
    try:
        import time
        start_time = time.time()
        
        results = []
        anomaly_count = 0
        
        for event in request.events:
            event_data = event.model_dump()
            result = inference_service.predict(event_data)
            
            # Store result
            global anomaly_counter
            anomaly_counter += 1
            result['anomaly_id'] = f"ANO-{anomaly_counter}"
            anomaly_store.append(result)
            
            if result.get('is_anomaly'):
                anomaly_count += 1
            
            results.append(InferenceResponse(
                event_id=result.get('event_id'),
                is_anomaly=result.get('is_anomaly', False),
                confidence=result.get('confidence', 0.0),
                risk_score=result.get('risk_score', 0.0),
                risk_level=result.get('risk_level', 'low'),
                baseline_score=result.get('baseline_score', 0.0),
                lstm_confidence=result.get('lstm_confidence', 0.0),
                flagged_by=result.get('flagged_by', 'none'),
                attack_type=result.get('attack_type'),
                reasons=result.get('reasons', []),
                suggested_action=result.get('suggested_action', 'Monitor')
            ))
        
        processing_time = time.time() - start_time
        
        return BatchInferenceResponse(
            results=results,
            processing_time=processing_time,
            total_anomalies=anomaly_count
        )
        
    except Exception as e:
        logger.error(f"Error in batch detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=PaginatedResponse)
async def list_anomalies(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    risk_level: Optional[str] = None,
    flagged_by: Optional[str] = None,
    resource_accessed: Optional[str] = None,
    geo_location: Optional[str] = None,
    auth_method: Optional[str] = None,
    device_type: Optional[str] = None,
):
    """
    List detected anomalies with pagination
    
    Query Parameters:
        - page: Page number (default 1)
        - page_size: Results per page (default 50, max 500)
        - risk_level: Filter by risk level
        - flagged_by: Filter by detection source (baseline, lstm, both)
        - resource_accessed: Filter by accessed resource
        - geo_location: Filter by geographic location
        - auth_method: Filter by authentication method
        - device_type: Filter by device type
    """
    try:
        # Filter results
        filtered = anomaly_store
        
        if risk_level:
            filtered = [a for a in filtered if a.get('risk_level') == risk_level]
        
        if flagged_by:
            filtered = [a for a in filtered if a.get('flagged_by') == flagged_by]
        
        if resource_accessed:
            filtered = [a for a in filtered if a.get('resource_accessed') == resource_accessed]
        
        if geo_location:
            filtered = [a for a in filtered if a.get('geo_location') == geo_location]
        
        if auth_method:
            filtered = [a for a in filtered if a.get('auth_method') == auth_method]
        
        if device_type:
            filtered = [a for a in filtered if a.get('device_type') == device_type]
        
        # Sort by timestamp (newest first)
        filtered = sorted(filtered, key=lambda x: str(x.get('timestamp', '')), reverse=True)
        
        # Calculate pagination
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
        logger.error(f"Error listing anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(anomaly_id: str):
    """
    Get detailed information about a specific anomaly
    
    Path Parameters:
        - anomaly_id: Anomaly identifier
    """
    try:
        # Search in store
        for anomaly in anomaly_store:
            if anomaly.get('anomaly_id') == anomaly_id or anomaly.get('event_id') == anomaly_id:
                return AnomalyResponse(
                    anomaly_id=anomaly.get('anomaly_id', anomaly_id),
                    event_id=anomaly.get('event_id'),
                    entity_id=anomaly.get('entity_id'),
                    timestamp=anomaly.get('timestamp'),
                    risk_score=anomaly.get('risk_score', 0.0),
                    confidence=anomaly.get('confidence', 0.0),
                    risk_level=anomaly.get('risk_level', 'low'),
                    baseline_score=anomaly.get('baseline_score', 0.0),
                    lstm_confidence=anomaly.get('lstm_confidence', 0.0),
                    attack_type=anomaly.get('attack_type'),
                    reasons=[{"reason": r, "confidence": 0.8, "source": anomaly.get('flagged_by')} for r in anomaly.get('reasons', [])],
                    flagged_by=anomaly.get('flagged_by', 'none'),
                    resource_accessed=anomaly.get('resource_accessed', ''),
                    geo_location=anomaly.get('geo_location', ''),
                    auth_method=anomaly.get('auth_method', ''),
                    device_type=anomaly.get('device_type', '')
                )
        
        raise HTTPException(status_code=404, detail=f"Anomaly {anomaly_id} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting anomaly: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_anomaly_statistics():
    """Get statistics about detected anomalies"""
    try:
        total = len(anomaly_store)
        anomalies_count = len([a for a in anomaly_store if a.get('is_anomaly')])
        
        risk_distribution = {
            'low': len([a for a in anomaly_store if a.get('risk_level') == 'low']),
            'medium': len([a for a in anomaly_store if a.get('risk_level') == 'medium']),
            'high': len([a for a in anomaly_store if a.get('risk_level') == 'high']),
            'critical': len([a for a in anomaly_store if a.get('risk_level') == 'critical']),
        }
        
        flagged_distribution = {
            'baseline': len([a for a in anomaly_store if a.get('flagged_by') == 'baseline']),
            'lstm': len([a for a in anomaly_store if a.get('flagged_by') == 'lstm']),
            'both': len([a for a in anomaly_store if a.get('flagged_by') == 'both']),
        }
        
        avg_confidence = sum(a.get('confidence', 0) for a in anomaly_store) / total if total > 0 else 0
        avg_baseline = sum(a.get('baseline_score', 0) for a in anomaly_store) / total if total > 0 else 0
        avg_lstm = sum(a.get('lstm_confidence', 0) for a in anomaly_store) / total if total > 0 else 0
        
        return {
            "total_events": total,
            "total_anomalies": anomalies_count,
            "anomaly_rate": anomalies_count / total if total > 0 else 0,
            "risk_distribution": risk_distribution,
            "flagged_distribution": flagged_distribution,
            "average_confidence": avg_confidence,
            "average_baseline_score": avg_baseline,
            "average_lstm_confidence": avg_lstm
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
