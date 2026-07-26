"""
Drift monitor service

Periodically computes feature drift and triggers retraining steps when drift is detected.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import List
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


class DriftMonitor:
    def __init__(self, data_service, inference_service, features: List[str] | None = None, check_interval: int = 3600, drift_threshold: float = 0.05):
        self.data_service = data_service
        self.inference_service = inference_service
        self.features = features or ['risk_score', 'session_duration', 'failed_login_attempts', 'location_changed', 'device_changed']
        self.check_interval = check_interval
        self.drift_threshold = drift_threshold
        self._stop_event = threading.Event()

    def check_drift(self) -> bool:
        try:
            from src.drift_detector import drift_triggered

            # Use processed logs if available, otherwise use cybersecurity_df
            df = None
            if self.data_service.processed_logs_df is not None:
                df = self.data_service.processed_logs_df
            elif self.data_service.cybersecurity_df is not None:
                df = self.data_service.cybersecurity_df

            if df is None or len(df) < 10:
                logger.debug("Not enough data for drift check")
                return False

            # Split into early/late windows
            mid = int(len(df) * 0.5)
            early = df.iloc[:mid].reset_index(drop=True)
            late = df.iloc[mid:].reset_index(drop=True)

            triggered = drift_triggered(early, late, self.features, threshold=self.drift_threshold)
            if triggered:
                logger.warning("Feature drift detected — triggering retraining workflow")
                self._trigger_retraining()
            return bool(triggered)
        except Exception:
            logger.exception("Error during drift check")
            return False

    def _trigger_retraining(self):
        try:
            # Retrain attack-type classifier
            try:
                from src.attack_type_classifier import train_attack_type_classifier
                train_attack_type_classifier()
                logger.info("Attack-type classifier retrained")
            except Exception:
                logger.exception("Failed to retrain attack-type classifier")

            # Rebuild baseline profiles
            try:
                from src.baseline_profiling import create_baseline_profile_artifact
                create_baseline_profile_artifact()
                logger.info("Baseline profiles rebuilt")
            except Exception:
                logger.exception("Failed to rebuild baseline profiles")

            # Ask inference service to reload models
            try:
                self.inference_service._load_models()
            except Exception:
                logger.exception("Failed to reload models after retraining")

        except Exception:
            logger.exception("Retraining workflow failed")

    def run_loop(self):
        while not self._stop_event.is_set():
            try:
                self.check_drift()
            except Exception:
                logger.exception("DriftMonitor loop error")
            time.sleep(self.check_interval)

    def stop(self):
        self._stop_event.set()
