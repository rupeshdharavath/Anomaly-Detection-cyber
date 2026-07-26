"""
Cold-start onboarding service

Accumulates recent events for new entities and builds baseline profile artifacts
when a minimum number of events is observed.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Dict, List
import pandas as pd
from pathlib import Path

from ..config import settings

logger = logging.getLogger(__name__)


class ColdStartService:
    def __init__(self, inference_service, data_service):
        self.inference_service = inference_service
        self.data_service = data_service
        self.buffers: Dict[str, List[Dict]] = {}
        self.lock = threading.Lock()

    def add_event(self, entity_id: str, event: Dict):
        """Add an event to the buffer for the given entity"""
        with self.lock:
            self.buffers.setdefault(entity_id, []).append(event)

    def process_buffers(self):
        """Check buffers and build baseline profiles when enough events are available"""
        with self.lock:
            to_build = [eid for eid, evs in self.buffers.items() if len(evs) >= getattr(self.inference_service, 'cold_start_min_events', 3)]

        for eid in to_build:
            try:
                with self.lock:
                    evs = list(self.buffers.pop(eid, []))

                # Build DataFrame
                df = pd.DataFrame(evs)
                # Use baseline_profiling to construct profile rows
                from src.baseline_profiling import build_baseline_profiles

                profiles_df = build_baseline_profiles(df)
                if profiles_df is not None and not profiles_df.empty:
                    profile_row = profiles_df.iloc[0:1]
                    # Load or create baseline file
                    baseline_path = Path(settings.MODELS_DIR) / Path(settings.BASELINE_PROFILES).name
                    try:
                        import pickle
                        if baseline_path.exists():
                            with open(baseline_path, 'rb') as f:
                                existing = pickle.load(f)
                            # existing might be dict or DataFrame
                            if isinstance(existing, dict):
                                existing.update({str(profile_row.iloc[0]['entity_id']): profile_row.iloc[0].to_dict()})
                                with open(baseline_path, 'wb') as f:
                                    pickle.dump(existing, f)
                            else:
                                # assume DataFrame
                                new_df = pd.concat([existing, profile_row], ignore_index=True)
                                with open(baseline_path, 'wb') as f:
                                    pickle.dump(new_df, f)
                        else:
                            baseline_path.parent.mkdir(parents=True, exist_ok=True)
                            with open(baseline_path, 'wb') as f:
                                pickle.dump(profile_row, f)

                        # Ask inference service to reload baseline profiles
                        try:
                            self.inference_service._load_models()
                        except Exception:
                            logger.exception("Failed to reload models after cold-start onboarding")

                        logger.info(f"Built baseline profile for entity {eid}")
                    except Exception:
                        logger.exception("Error saving baseline profile during cold-start processing")

            except Exception:
                logger.exception(f"Error processing cold-start for entity {eid}")

    def run_loop(self, interval_seconds: int = 60):
        while True:
            try:
                self.process_buffers()
            except Exception:
                logger.exception("ColdStartService loop error")
            time.sleep(interval_seconds)
