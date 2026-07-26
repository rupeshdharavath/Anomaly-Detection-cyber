"""
Inference Service
Handles LSTM and Baseline anomaly detection
"""

import logging
import pickle
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import sys
import os
from collections import defaultdict

from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ..config import settings
from src.attack_type_classifier import load_attack_type_assets, predict_attack_type
from src.attack_type_classifier import load_attack_type_assets, predict_attack_type

logger = logging.getLogger(__name__)

# LSTM training architecture constants
NUMERIC_COLUMNS = [
    "session_duration",
    "failed_login_attempts",
    "normal_login_start",
    "normal_failed_login_attempts",
    "login_hour",
    "risk_score",
]
BOOLEAN_COLUMNS = [
    "location_changed",
    "device_changed",
    "auth_changed",
    "login_time_changed",
    "long_session",
    "high_failed_login",
    "resource_changed",
]
CATEGORICAL_COLUMNS = [
    "entity_type",
    "geo_location",
    "resource_accessed",
    "auth_method",
    "department",
    "office",
    "device_type",
    "operating_system",
    "browser",
]
WINDOW_SIZE = 5


class InferenceService:
    """Service for anomaly detection inference"""
    
    def __init__(self):
        """Initialize inference service"""
        self.lstm_model = None
        self.lstm_threshold = None
        self.baseline_profiles = None
        self.scaler = None
        self.feature_columns = None
        self.lstm_feature_columns = None  # LSTM-specific 57-feature columns (one-hot expanded)
        self.attack_type_model, self.attack_type_encoder, self.attack_type_cat_encoders, self.attack_type_feature_columns = load_attack_type_assets()
        self.models_loaded = False
        self.cold_start_entities: set[str] = set()
        # COLD_START_MIN_EVENTS may live in src/config.py for training/runtime defaults — fall back if missing
        try:
            self.cold_start_min_events = settings.COLD_START_MIN_EVENTS
        except Exception:
            try:
                from src.config import COLD_START_MIN_EVENTS
                self.cold_start_min_events = COLD_START_MIN_EVENTS
            except Exception:
                self.cold_start_min_events = 3
        
        # Entity event buffer: maps entity_id -> list of last WINDOW_SIZE feature vectors
        self.entity_event_buffer = defaultdict(lambda: [])
        
        self._load_models()
    
    def _load_models(self):
        """Load trained models and artifacts"""
        baseline_loaded = False

        # Load LSTM model if available
        try:
            from tensorflow import keras
            if os.path.exists(settings.LSTM_MODEL):
                self.lstm_model = keras.models.load_model(settings.LSTM_MODEL)
                logger.info(f"✅ LSTM model loaded from {settings.LSTM_MODEL}")
            else:
                logger.warning(f"⚠️  LSTM model not found at {settings.LSTM_MODEL}")
        except ImportError:
            logger.warning("⚠️  TensorFlow not available - LSTM detection disabled")
        except Exception as e:
            logger.error(f"⚠️  Error loading LSTM model: {e}")

        # Load LSTM threshold
        try:
            if os.path.exists(settings.LSTM_THRESHOLD):
                with open(settings.LSTM_THRESHOLD, 'rb') as f:
                    threshold_data = pickle.load(f)
                if isinstance(threshold_data, dict):
                    self.lstm_threshold = float(threshold_data.get('threshold', 0.5))
                else:
                    self.lstm_threshold = float(threshold_data)
                logger.info(f"✅ LSTM threshold loaded ({self.lstm_threshold})")
            else:
                self.lstm_threshold = 0.5  # Default threshold
        except Exception as e:
            logger.warning(f"⚠️  Could not load LSTM threshold: {e}")
            self.lstm_threshold = 0.5

        # Load baseline profiles
        try:
            if os.path.exists(settings.BASELINE_PROFILES):
                with open(settings.BASELINE_PROFILES, 'rb') as f:
                    baseline_data = pickle.load(f)

                if isinstance(baseline_data, pd.DataFrame):
                    # Handle DataFrame with possible duplicate indices
                    self.baseline_profiles = {}
                    if 'entity_id' in baseline_data.columns:
                        # Group by entity_id and take first/most recent profile
                        for entity_id, group in baseline_data.groupby('entity_id'):
                            self.baseline_profiles[str(entity_id)] = group.iloc[-1].to_dict()
                    else:
                        # Use index as entity_id
                        baseline_data_reset = baseline_data.reset_index()
                        if 'index' in baseline_data_reset.columns:
                            baseline_data_reset = baseline_data_reset.rename(columns={'index': 'entity_id'})
                        for _, row in baseline_data_reset.iterrows():
                            entity_id = str(row.get('entity_id', f'entity_{_}'))
                            self.baseline_profiles[entity_id] = row.to_dict()
                else:
                    # Already a dict or similar
                    self.baseline_profiles = baseline_data if isinstance(baseline_data, dict) else {}

                baseline_loaded = bool(self.baseline_profiles)
                logger.info(f"✅ Baseline profiles loaded ({len(self.baseline_profiles)} entities)")
            else:
                logger.warning(f"⚠️  Baseline profiles not found at {settings.BASELINE_PROFILES}")
        except Exception as e:
            logger.error(f"⚠️  Error loading baseline profiles: {e}")
            self.baseline_profiles = None

        # Load scaler
        try:
            if os.path.exists(settings.SCALER):
                with open(settings.SCALER, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info("✅ Scaler loaded")
        except Exception as e:
            logger.warning(f"⚠️  Could not load scaler: {e}")
            self.scaler = None

        # Load feature columns
        try:
            if os.path.exists(settings.FEATURE_COLUMNS):
                with open(settings.FEATURE_COLUMNS, 'rb') as f:
                    self.feature_columns = pickle.load(f)
                logger.info(f"✅ Feature columns loaded ({len(self.feature_columns)} features)")
        except Exception as e:
            logger.warning(f"⚠️  Could not load feature columns: {e}")
            self.feature_columns = None

        # Load LSTM-specific feature columns (57 one-hot expanded features)
        try:
            if os.path.exists(settings.LSTM_FEATURE_COLUMNS):
                with open(settings.LSTM_FEATURE_COLUMNS, 'rb') as f:
                    self.lstm_feature_columns = pickle.load(f)
                logger.info(f"✅ LSTM feature columns loaded ({len(self.lstm_feature_columns)} features)")
            else:
                logger.warning(f"⚠️  LSTM feature columns not found at {settings.LSTM_FEATURE_COLUMNS}")
                self.lstm_feature_columns = None
        except Exception as e:
            logger.warning(f"⚠️  Could not load LSTM feature columns: {e}")
            self.lstm_feature_columns = None

        self.models_loaded = baseline_loaded or bool(self.lstm_model)
    
    def _normalize_attack_type(self, attack_type: str) -> str:
        """
        Normalize attack type to enum format (lowercase with underscores)
        
        Args:
            attack_type: Attack type string (may have spaces, capitals, etc.)
            
        Returns:
            Normalized attack type string
        """
        if not attack_type or attack_type.lower() == 'unknown':
            return 'unknown'
        
        # Mapping from various formats to enum format
        mapping = {
            'brute_force': 'brute_force',
            'brute force': 'brute_force',
            'bruteforce': 'brute_force',
            'impossible_travel': 'impossible_travel',
            'impossible travel': 'impossible_travel',
            'credential_stuffing': 'credential_stuffing',
            'credential stuffing': 'credential_stuffing',
            'device_spoofing': 'device_spoofing',
            'device spoofing': 'device_spoofing',
            'lateral_movement': 'lateral_movement',
            'lateral movement': 'lateral_movement',
            'low_and_slow': 'low_and_slow',
            'low and slow': 'low_and_slow',
            'insider_threat': 'insider_threat',
            'insider threat': 'insider_threat',
            'slow_credential': 'slow_credential',
            'slow credential': 'slow_credential',
            'unknown': 'unknown',
        }
        
        normalized = attack_type.lower().replace(' ', '_')
        return mapping.get(normalized, 'unknown')
    
    def predict(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict anomaly for a single event
        
        Args:
            event_data: Event information
            
        Returns:
            Prediction result with scores and reasoning
        """
        try:
            if not self.models_loaded:
                return self._error_response(event_data, "Models not loaded")
            
            # Get baseline score
            baseline_score, baseline_reasons = self._score_baseline(event_data)
            
            # Get LSTM score
            lstm_confidence = self._score_lstm(event_data) if self.lstm_model else None
            
            # Ensemble decision
            result = self._ensemble_decision(
                event_data,
                baseline_score,
                baseline_reasons,
                lstm_confidence
            )
            
            # Track cold-start entities
            if event_data.get('entity_id') and event_data.get('entity_id') not in self.baseline_profiles:
                self.cold_start_entities.add(str(event_data.get('entity_id')))
            
            # Predict attack type if models are available
            if self.attack_type_model is not None and self.attack_type_encoder is not None and self.attack_type_cat_encoders is not None and self.attack_type_feature_columns is not None:
                try:
                    predicted_attack_type = predict_attack_type(
                        event_data,
                        self.attack_type_model,
                        self.attack_type_encoder,
                        self.attack_type_cat_encoders,
                        self.attack_type_feature_columns,
                    )
                    if predicted_attack_type:
                        # Normalize attack type to enum format
                        result['attack_type'] = self._normalize_attack_type(predicted_attack_type)
                except Exception as e:
                    logger.warning(f"Error predicting attack type: {e}")
                    result['attack_type'] = 'unknown'
            
            return result
            
        except Exception as e:
            logger.error(f"Error during inference: {e}")
            return self._error_response(event_data, str(e))
    
    def _score_baseline(self, event_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        Score event against baseline profile
        
        Returns:
            Tuple of (score, reasons)
        """
        try:
            entity_id = event_data.get('entity_id')
            reasons = []
            score = 0.0
            
            if not entity_id or entity_id not in self.baseline_profiles:
                return 2.0, ["Unknown entity - cold start detected"]
            
            profile = self.baseline_profiles[entity_id]
            
            # Compare against the stored baseline mode values
            normal_resource = profile.get('resource_accessed_mode') or profile.get('normal_resources') or []
            normal_location = profile.get('geo_location_mode') or profile.get('normal_location')
            normal_auth_method = profile.get('auth_method_mode') or profile.get('normal_auth_methods') or []
            session_mean = profile.get('session_duration_mean') or profile.get('session_mean')
            session_std = profile.get('session_duration_std') or profile.get('session_std')

            if isinstance(normal_resource, list):
                resource_match = event_data.get('resource_accessed') in normal_resource
            else:
                resource_match = event_data.get('resource_accessed') == normal_resource

            if not resource_match:
                score += 2.0
                reasons.append("Unauthorized resource access (Insider threat indicator)")

            if event_data.get('geo_location') != normal_location:
                score += 1.5
                reasons.append("Impossible travel detected (Location change)")

            if event_data.get('auth_method') not in normal_auth_method:
                score += 1.0
                reasons.append("Unusual authentication method")

            session_duration = event_data.get('session_duration', 0)
            if session_mean is not None and session_std is not None:
                mean = float(session_mean)
                std = float(session_std)
                tolerance = max(std * 1.5, 1.0)

                if abs(session_duration - mean) > 2.5 * tolerance:
                    score += 1.5
                    reasons.append(f"Extreme session duration anomaly (Expected ~{mean:.0f}s, got {session_duration}s)")
                elif abs(session_duration - mean) > 1.5 * tolerance:
                    score += 0.5
                    reasons.append(f"Moderate session duration drift (Expected ~{mean:.0f}s, got {session_duration}s)")
            
            return score, reasons
            
        except Exception as e:
            logger.error(f"Error in baseline scoring: {e}")
            return 0.0, [f"Baseline scoring error: {str(e)}"]
    
    def _score_lstm(self, event_data: Dict[str, Any]) -> Optional[float]:
        """
        Score event using LSTM model with proper sequence windowing
        
        Maintains a sliding window of last WINDOW_SIZE (5) events per entity.
        Passes 3D tensor (1, 5, 57) to the model.
        
        Returns:
            LSTM confidence score (0-1) or None if model unavailable
        """
        try:
            if not self.lstm_model or not self.lstm_feature_columns:
                return None
            
            entity_id = event_data.get('entity_id')
            if not entity_id:
                return None
            
            # Extract features as a 1D vector (must be 57 elements)
            features = self._extract_features(event_data)
            if features is None or len(features) != len(self.lstm_feature_columns):
                logger.error(
                    f"Feature extraction failed: expected {len(self.lstm_feature_columns)} features, "
                    f"got {len(features) if features else 0}"
                )
                return None
            
            # Add to entity's event buffer
            self.entity_event_buffer[entity_id].append(features)
            
            # Keep only last WINDOW_SIZE events
            if len(self.entity_event_buffer[entity_id]) > WINDOW_SIZE:
                self.entity_event_buffer[entity_id] = self.entity_event_buffer[entity_id][-WINDOW_SIZE:]
            
            # If we don't have enough history, pad with zeros (first few events for cold start)
            window = self.entity_event_buffer[entity_id].copy()
            while len(window) < WINDOW_SIZE:
                window.insert(0, [0.0] * len(self.lstm_feature_columns))
            
            # Build 3D sequence: (1, WINDOW_SIZE, num_features)
            sequence = np.array([window], dtype=np.float32)  # Shape: (1, 5, 57)
            
            # Verify shape matches model expectation
            if sequence.shape != (1, WINDOW_SIZE, len(self.lstm_feature_columns)):
                logger.error(f"Shape mismatch: expected (1, {WINDOW_SIZE}, {len(self.lstm_feature_columns)}), got {sequence.shape}")
                return None
            
            # Predict
            try:
                prediction = self.lstm_model.predict(sequence, verbose=0)
                
                if isinstance(prediction, np.ndarray):
                    confidence = float(np.asarray(prediction).reshape(-1)[0])
                elif isinstance(prediction, list):
                    if len(prediction) > 0:
                        first = prediction[0]
                        confidence = float(first[0] if isinstance(first, (list, tuple, np.ndarray)) else first)
                    else:
                        return None
                else:
                    confidence = float(prediction)
                
                # Clamp to [0, 1]
                confidence = max(0.0, min(1.0, confidence))
                return confidence
                
            except Exception as e:
                logger.error(f"Model prediction failed: {e} (shape: {sequence.shape})")
                return None
            
        except Exception as e:
            logger.error(f"Error in LSTM scoring: {e}")
            return None
    
    def _extract_features(self, event_data: Dict[str, Any]) -> Optional[List[float]]:
        """
        Extract full 57-feature vector from event data, matching training pipeline.
        
        Builds:
        - 6 numeric features (scaled by scaler)
        - 7 boolean features (0/1)
        - ~38 one-hot categorical features (9 categorical columns)
        
        Uses self.lstm_feature_columns (57 one-hot expanded) for reconstruction,
        NOT self.feature_columns (22 raw baseline columns).
        
        Returns:
            List of 57 floats or None on error
        """
        try:
            if not self.lstm_feature_columns:
                logger.error("LSTM feature columns not loaded - cannot extract features")
                return None
            
            features = []
            
            # Extract numeric features (first 6 in training)
            numeric_vals = []
            for col in NUMERIC_COLUMNS:
                if col in event_data:
                    numeric_vals.append(float(event_data[col]))
                else:
                    numeric_vals.append(0.0)
            
            # Scale numeric features using the fitted scaler
            if self.scaler and len(numeric_vals) == len(NUMERIC_COLUMNS):
                try:
                    scaled = self.scaler.transform([numeric_vals])[0]
                    features.extend(scaled)
                except Exception as e:
                    logger.warning(f"Scaler transform failed: {e}, using raw values")
                    features.extend(numeric_vals)
            else:
                features.extend(numeric_vals)
            
            # Extract boolean features (7 columns)
            for col in BOOLEAN_COLUMNS:
                val = event_data.get(col, 0)
                features.append(float(val if val else 0))
            
            # Extract and one-hot encode categorical features
            # Use lstm_feature_columns to find all one-hot categories
            for col in CATEGORICAL_COLUMNS:
                col_val = str(event_data.get(col, '')).strip()
                
                # Get all possible categories for this column from training (lstm_feature_columns)
                col_categories = set()
                for feature_name in self.lstm_feature_columns:
                    if feature_name.startswith(f"{col}_"):
                        # Extract the category value (format is "col_category")
                        category = feature_name[len(col)+1:]
                        col_categories.add(category)
                
                # One-hot encode this categorical value
                for category in sorted(col_categories):
                    one_hot = 1.0 if col_val == category else 0.0
                    features.append(one_hot)
            
            # Verify length matches LSTM expected feature count
            if len(features) != len(self.lstm_feature_columns):
                logger.error(
                    f"Feature count mismatch: extracted {len(features)}, "
                    f"expected {len(self.lstm_feature_columns)}. Feature extraction failed."
                )
                return None
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    def _ensemble_decision(
        self,
        event_data: Dict[str, Any],
        baseline_score: float,
        baseline_reasons: List[str],
        lstm_confidence: Optional[float]
    ) -> Dict[str, Any]:
        """
        Make ensemble decision combining baseline and LSTM
        
        Returns:
            Combined prediction result
        """
        baseline_threshold = settings.ANOMALY_THRESHOLD
        lstm_threshold = self.lstm_threshold or settings.ANOMALY_THRESHOLD
        
        # Normalize scores
        baseline_normalized = min(baseline_score / 4.0, 1.0)  # Max baseline score ~4.0
        valid_lstm = isinstance(lstm_confidence, (int, float))
        lstm_normalized = float(lstm_confidence) if valid_lstm else baseline_normalized

        # Weighted ensemble or pure baseline fallback when LSTM is unavailable
        if not valid_lstm:
            ensemble_score = baseline_normalized
        else:
            ensemble_score = (
                baseline_normalized * settings.BASELINE_WEIGHT +
                lstm_normalized * settings.LSTM_WEIGHT
            )
        
        # Determine if anomaly
        baseline_flag = baseline_score > baseline_threshold
        lstm_flag = valid_lstm and lstm_confidence > lstm_threshold

        is_anomaly = bool(baseline_flag or lstm_flag)
        attack_type = self._infer_attack_type(event_data, baseline_score, lstm_confidence)

        # Ensure there is at least one anomaly reason when a flag is active
        baseline_reasons = baseline_reasons or []
        if baseline_flag and not baseline_reasons:
            baseline_reasons = ["Baseline anomaly detected"]

        # Determine flagged_by
        if baseline_flag and lstm_flag:
            flagged_by = "both"
            confidence = 0.95
            combined_reasons = baseline_reasons
        elif lstm_flag:
            flagged_by = "lstm"
            confidence = lstm_normalized
            combined_reasons = baseline_reasons + ["LSTM sequence anomaly detected"]
        elif baseline_flag:
            flagged_by = "baseline"
            confidence = baseline_normalized
            combined_reasons = baseline_reasons
        else:
            flagged_by = "none"
            confidence = 1.0 - ensemble_score
            combined_reasons = ["Normal behavior"]

        # Calculate risk level
        risk_level = self._risk_level(ensemble_score)

        return {
            "event_id": event_data.get('event_id', 'unknown'),
            "entity_id": event_data.get('entity_id', ''),
            "timestamp": event_data.get('timestamp', datetime.now()),
            "is_anomaly": bool(is_anomaly),
            "confidence": float(confidence),
            "risk_score": float(ensemble_score),
            "risk_level": risk_level,
            "baseline_score": float(baseline_score),
            "lstm_confidence": float(lstm_confidence or 0.0),
            "flagged_by": flagged_by,
            "attack_type": attack_type or "unknown",
            "reasons": combined_reasons,
            "suggested_action": self._suggest_action(risk_level, is_anomaly),
            "device_type": event_data.get('device_type', ''),
            "failed_login_attempts": int(event_data.get('failed_login_attempts', 0)),
            "session_duration": int(event_data.get('session_duration', 0))
        }
    
    def _risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _suggest_action(self, risk_level: str, is_anomaly: bool) -> str:
        """Suggest action based on risk level"""
        if not is_anomaly:
            return "Monitor"
        elif risk_level == "critical":
            return "Block immediately"
        elif risk_level == "high":
            return "Investigate and isolate"
        elif risk_level == "medium":
            return "Review and investigate"
        else:
            return "Log and monitor"

    def _infer_attack_type(self, event_data: Dict[str, Any], baseline_score: float, lstm_confidence: Optional[float]) -> str:
        """Infer a likely attack type for display"""
        if event_data.get('failed_login_attempts', 0) >= 5:
            return 'Brute Force'
        if event_data.get('geo_location') and event_data.get('geo_location') not in event_data.get('normal_location', ''):
            return 'Impossible Travel'
        if event_data.get('resource_accessed') in ['Finance DB', 'Internal Server', 'Database'] and baseline_score > 1.0:
            return 'Lateral Movement'
        if event_data.get('session_duration', 0) >= 1800:
            return 'Long Session'
        if lstm_confidence and lstm_confidence > 0.8:
            return 'Credential Stuffing'
        return 'Unknown'
    
    def _error_response(self, event_data: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "event_id": event_data.get('event_id', 'unknown'),
            "entity_id": event_data.get('entity_id', ''),
            "timestamp": event_data.get('timestamp', datetime.now()),
            "is_anomaly": False,
            "confidence": 0.0,
            "risk_score": 0.0,
            "risk_level": "low",
            "baseline_score": 0.0,
            "lstm_confidence": 0.0,
            "flagged_by": "none",
            "attack_type": event_data.get('attack_type', 'unknown'),
            "reasons": [f"Error: {error}"],
            "suggested_action": "Review system status",
            "resource_accessed": event_data.get('resource_accessed', ''),
            "geo_location": event_data.get('geo_location', ''),
            "auth_method": event_data.get('auth_method', ''),
            "device_type": event_data.get('device_type', ''),
            "failed_login_attempts": int(event_data.get('failed_login_attempts', 0)),
            "session_duration": int(event_data.get('session_duration', 0)),
            "error": error
        }
