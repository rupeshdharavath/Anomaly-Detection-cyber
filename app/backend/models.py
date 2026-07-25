"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackType(str, Enum):
    """Attack type enumeration"""
    BRUTE_FORCE = "brute_force"
    IMPOSSIBLE_TRAVEL = "impossible_travel"
    CREDENTIAL_STUFFING = "credential_stuffing"
    DEVICE_SPOOFING = "device_spoofing"
    LATERAL_MOVEMENT = "lateral_movement"
    LOW_AND_SLOW = "low_and_slow"
    INSIDER_THREAT = "insider_threat"
    SLOW_CREDENTIAL = "slow_credential"
    UNKNOWN = "unknown"


# ==================== Events ====================

class EventBase(BaseModel):
    """Base event model"""
    timestamp: datetime
    entity_id: str
    resource_accessed: str
    geo_location: str
    auth_method: str
    device_type: str
    failed_login_attempts: int = 0
    session_duration: int = 0


class EventCreate(EventBase):
    """Event creation model"""
    pass


class EventResponse(EventBase):
    """Event response model"""
    event_id: str
    risk_score: float
    
    class Config:
        from_attributes = True


# ==================== Anomalies ====================

class AnomalyDetail(BaseModel):
    """Anomaly detail"""
    reason: str
    confidence: float
    source: str  # "baseline", "lstm", or "both"


class AnomalyBase(BaseModel):
    """Base anomaly model"""
    event_id: str
    entity_id: str
    timestamp: datetime
    risk_score: float
    confidence: float
    risk_level: RiskLevel
    baseline_score: float
    lstm_confidence: float


class AnomalyResponse(AnomalyBase):
    """Anomaly response model"""
    anomaly_id: str
    attack_type: Optional[AttackType] = None
    reasons: List[AnomalyDetail]
    flagged_by: str  # "baseline", "lstm", or "both"
    resource_accessed: str
    geo_location: str
    auth_method: str
    device_type: str
    
    class Config:
        from_attributes = True


class AnomalyFilter(BaseModel):
    """Anomaly filter model"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    entity_id: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    attack_type: Optional[AttackType] = None
    flagged_by: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


# ==================== Alerts ====================

class AlertBase(BaseModel):
    """Base alert model"""
    anomaly_id: str
    severity: RiskLevel
    message: str
    action_required: bool


class AlertCreate(AlertBase):
    """Alert creation model"""
    pass


class AlertResponse(AlertBase):
    """Alert response model"""
    alert_id: str
    entity_id: str
    risk_score: float
    attack_type: Optional[AttackType] = None
    confidence: float
    flagged_by: str
    created_at: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    """Alert update model"""
    acknowledged: bool
    acknowledged_by: Optional[str] = None


# ==================== Analytics ====================

class RiskDistribution(BaseModel):
    """Risk distribution"""
    low: int
    medium: int
    high: int
    critical: int


class TimeSeriesPoint(BaseModel):
    """Time series data point"""
    timestamp: datetime
    value: float
    count: int


class AnalyticsResponse(BaseModel):
    """Analytics response"""
    total_events: int
    total_anomalies: int
    anomaly_rate: float
    risk_distribution: RiskDistribution
    top_attack_types: List[Dict[str, Any]]
    confidence_stats: Dict[str, float]
    time_series: List[TimeSeriesPoint]


# ==================== Entities ====================

class EntityProfile(BaseModel):
    """User/Entity profile"""
    entity_id: str
    entity_type: str  # "user" or "device"
    name: str
    department: Optional[str] = None
    office: Optional[str] = None
    device_type: Optional[str] = None
    os: Optional[str] = None
    browser: Optional[str] = None


class EntityStats(BaseModel):
    """Entity statistics"""
    entity_id: str
    total_events: int
    anomalies_count: int
    anomaly_rate: float
    average_confidence: float
    common_attack_types: List[str]
    risk_level: RiskLevel


class EntityDetailResponse(BaseModel):
    """Entity detail response"""
    profile: EntityProfile
    stats: EntityStats
    recent_anomalies: List[AnomalyResponse]
    timeline: List[TimeSeriesPoint]


# ==================== Models ====================

class ModelInfo(BaseModel):
    """Model information"""
    name: str
    type: str  # "baseline" or "lstm"
    version: str
    created_at: datetime
    status: str  # "loaded" or "error"
    parameters: Dict[str, Any]


class ModelsResponse(BaseModel):
    """Models response"""
    baseline: ModelInfo
    lstm: ModelInfo
    ensemble_config: Dict[str, float]


# ==================== Inference ====================

class InferenceRequest(BaseModel):
    """Inference request"""
    event_id: str
    timestamp: datetime
    entity_id: str
    resource_accessed: str
    geo_location: str
    auth_method: str
    device_type: str
    failed_login_attempts: int = 0
    session_duration: int = 0
    additional_features: Optional[Dict[str, Any]] = None


class InferenceResponse(BaseModel):
    """Inference response"""
    event_id: str
    is_anomaly: bool
    confidence: float
    risk_score: float
    risk_level: RiskLevel
    baseline_score: float
    lstm_confidence: float
    flagged_by: str  # "baseline", "lstm", or "both"
    attack_type: Optional[AttackType] = None
    reasons: List[str]
    suggested_action: str


class BatchInferenceRequest(BaseModel):
    """Batch inference request"""
    events: List[InferenceRequest]


class BatchInferenceResponse(BaseModel):
    """Batch inference response"""
    results: List[InferenceResponse]
    processing_time: float
    total_anomalies: int


# ==================== Health ====================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    services: Dict[str, str]
    models_loaded: bool
    data_files_present: bool


# ==================== Pagination ====================

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
