"""
Alert Service
Manages alert generation and tracking
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class Alert:
    """In-memory Alert storage (would use database in production)"""
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.alert_counter = 0
    
    def create_alert(
        self,
        anomaly_id: str,
        entity_id: str,
        risk_score: float,
        confidence: float,
        attack_type: Optional[str],
        flagged_by: str,
        severity: str,
        message: str,
        action_required: bool
    ) -> Dict[str, Any]:
        """Create new alert"""
        self.alert_counter += 1
        normalized_attack_type = self._normalize_attack_type(attack_type)
        normalized_severity = self._normalize_severity(severity)

        alert = {
            "alert_id": f"ALT-{self.alert_counter}",
            "anomaly_id": anomaly_id,
            "entity_id": entity_id,
            "risk_score": risk_score,
            "confidence": confidence,
            "attack_type": normalized_attack_type,
            "flagged_by": flagged_by,
            "severity": normalized_severity,
            "message": message,
            "action_required": action_required,
            "created_at": datetime.now().isoformat(),
            "acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None
        }
        self.alerts.append(alert)
        return alert
    
    def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return sorted(self.alerts, key=lambda x: x['created_at'], reverse=True)[:limit]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Optional[Dict[str, Any]]:
        """Acknowledge alert"""
        for alert in self.alerts:
            if alert['alert_id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_by'] = acknowledged_by
                alert['acknowledged_at'] = datetime.now().isoformat()
                return alert
        return None

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity values to valid enum values."""
        if not severity:
            return 'medium'
        normalized = severity.strip().lower()
        if normalized in {'critical', 'high', 'medium', 'low'}:
            return normalized
        if normalized in {'warning', 'warn'}:
            return 'medium'
        if normalized == 'info':
            return 'low'
        return 'medium'

    def _normalize_attack_type(self, attack_type: Optional[str]) -> str:
        """Normalize attack type values to valid enum values."""
        if not attack_type:
            return 'unknown'

        normalized = str(attack_type).strip().lower().replace(' ', '_')
        valid_attack_types = {
            'brute_force',
            'impossible_travel',
            'credential_stuffing',
            'device_spoofing',
            'lateral_movement',
            'low_and_slow',
            'insider_threat',
            'slow_credential',
            'unknown',
        }
        if normalized in valid_attack_types:
            return normalized
        if normalized == 'long_session':
            return 'slow_credential'
        if normalized == 'brute force':
            return 'brute_force'
        return 'unknown'


class AlertService:
    """Service for managing alerts"""
    
    def __init__(self, data_service):
        """Initialize alert service"""
        self.data_service = data_service
        self.alert_store = Alert()

    def seed_initial_alerts(self, limit: int = 50):
        """Seed initial alerts from high-risk historical events"""
        if self.alert_store.alerts:
            return

        events = self.data_service.get_top_risk_events(limit)
        for event in events:
            self.generate_alert_from_anomaly({
                'anomaly_id': event.get('event_id', f"evt-{event.get('entity_id', 'unknown')}-{event.get('timestamp')}"),
                'entity_id': event.get('entity_id', 'unknown'),
                'risk_score': float(event.get('risk_score', 0.0) or 0.0),
                'confidence': min(max(float(event.get('risk_score', 0.0) or 0.0), 0.0), 1.0),
                'attack_type': str(event.get('attack_type')) if event.get('attack_type') else 'unknown',
                'flagged_by': 'baseline',
                'department': event.get('department'),
                'resource_accessed': event.get('resource_accessed'),
                'geo_location': event.get('geo_location'),
                'auth_method': event.get('auth_method'),
                'device_type': event.get('device_type'),
                'failed_login_attempts': int(event.get('failed_login_attempts') or 0),
                'session_duration': int(event.get('session_duration') or 0),
                'reasons': [
                    "High historical risk score",
                    "Unusual access pattern"
                ],
                'suggested_action': 'Review and investigate'
            })
    
    def generate_alert_from_anomaly(self, anomaly: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate alert from anomaly detection result
        
        Args:
            anomaly: Anomaly detection result
            
        Returns:
            Generated alert
        """
        try:
            risk_level = anomaly.get('risk_level', 'low')
            confidence = anomaly.get('confidence', 0.0)
            reasons = anomaly.get('reasons', [])
            
            # Map risk level to severity
            severity_map = {
                'low': 'info',
                'medium': 'warning',
                'high': 'critical',
                'critical': 'critical'
            }
            severity = severity_map.get(risk_level, 'warning')
            
            # Create message
            entity_id = anomaly.get('entity_id', 'unknown')
            resource = anomaly.get('resource_accessed', 'unknown')
            message = f"Anomaly detected for {entity_id}: Accessing {resource} ({risk_level.upper()})"
            
            # Determine if action required
            action_required = risk_level in ['high', 'critical']
            
            # Create alert
            alert = self.alert_store.create_alert(
                anomaly_id=anomaly.get('anomaly_id', anomaly.get('event_id', 'unknown')),
                entity_id=anomaly.get('entity_id', 'unknown'),
                risk_score=anomaly.get('risk_score', 0.0),
                confidence=anomaly.get('confidence', 0.0),
                attack_type=anomaly.get('attack_type'),
                flagged_by=anomaly.get('flagged_by', 'none'),
                severity=severity,
                message=message,
                action_required=action_required
            )
            
            logger.info(f"✅ Alert created: {alert['alert_id']} ({severity})")
            return alert
            
        except Exception as e:
            logger.error(f"Error generating alert: {e}")
            return None
    
    def get_active_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get active (unacknowledged) alerts"""
        all_alerts = self.alert_store.get_alerts(limit * 2)
        active = [a for a in all_alerts if not a['acknowledged']]
        return active[:limit]
    
    def get_all_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all alerts"""
        return self.alert_store.get_alerts(limit)
    
    def acknowledge_alert(self, alert_id: str, user: str) -> Optional[Dict[str, Any]]:
        """Acknowledge alert"""
        alert = self.alert_store.acknowledge_alert(alert_id, user)
        if alert:
            logger.info(f"✅ Alert acknowledged: {alert_id} by {user}")
        return alert

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity values to valid enum values."""
        if not severity:
            return 'medium'
        normalized = severity.strip().lower()
        if normalized in {'critical', 'high', 'medium', 'low'}:
            return normalized
        if normalized in {'warning', 'warn'}:
            return 'medium'
        if normalized == 'info':
            return 'low'
        return 'medium'

    def _normalize_attack_type(self, attack_type: Optional[str]) -> str:
        """Normalize attack type values to valid enum values."""
        if not attack_type:
            return 'unknown'

        normalized = str(attack_type).strip().lower().replace(' ', '_')
        valid_attack_types = {
            'brute_force',
            'impossible_travel',
            'credential_stuffing',
            'device_spoofing',
            'lateral_movement',
            'low_and_slow',
            'insider_threat',
            'slow_credential',
            'unknown',
        }
        if normalized in valid_attack_types:
            return normalized
        if normalized == 'long_session':
            return 'slow_credential'
        if normalized == 'brute force':
            return 'brute_force'
        return 'unknown'
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        all_alerts = self.alert_store.alerts
        
        severity_count = {
            'info': 0,
            'warning': 0,
            'critical': 0
        }
        
        for alert in all_alerts:
            severity = alert.get('severity', 'warning')
            severity_count[severity] = severity_count.get(severity, 0) + 1
        
        unacknowledged = len([a for a in all_alerts if not a['acknowledged']])
        
        return {
            "total_alerts": len(all_alerts),
            "unacknowledged": unacknowledged,
            "severity_distribution": severity_count,
            "action_required_count": len([a for a in all_alerts if a['action_required'] and not a['acknowledged']])
        }
