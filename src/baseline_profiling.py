from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT / "data" / "raw" / "cybersecurity_dataset.csv"
PROFILE_PATH = ROOT / "trained_models" / "baseline_profile.pkl"

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


@dataclass
class BaselineProfile:
    entity_id: str
    row_count: int
    numeric_means: dict[str, float]
    numeric_stds: dict[str, float]
    categorical_modes: dict[str, str]
    allowed_resources: list[str]
    allowed_locations: list[str]
    allowed_auth_methods: list[str]
    allowed_devices: list[str]


def build_baseline_profiles(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    if "timestamp" in working.columns:
        working["timestamp"] = pd.to_datetime(working["timestamp"], errors="coerce")
        working = working.sort_values(["entity_id", "timestamp"])

    rows: list[dict[str, Any]] = []
    for entity_id, group in working.groupby("entity_id", sort=False):
        profile: dict[str, Any] = {
            "entity_id": entity_id,
            "row_count": int(len(group)),
        }

        for column in NUMERIC_COLUMNS:
            if column in group.columns:
                values = pd.to_numeric(group[column], errors="coerce").fillna(0.0)
                profile[f"{column}_mean"] = float(values.mean())
                profile[f"{column}_std"] = float(values.std(ddof=0))

        for column in CATEGORICAL_COLUMNS:
            if column in group.columns:
                mode_series = group[column].astype(str).mode(dropna=True)
                profile[f"{column}_mode"] = mode_series.iloc[0] if not mode_series.empty else ""

        profile["allowed_resources"] = sorted(group.get("resource_accessed", pd.Series(dtype=str)).astype(str).dropna().unique().tolist())
        profile["allowed_locations"] = sorted(group.get("geo_location", pd.Series(dtype=str)).astype(str).dropna().unique().tolist())
        profile["allowed_auth_methods"] = sorted(group.get("auth_method", pd.Series(dtype=str)).astype(str).dropna().unique().tolist())
        profile["allowed_devices"] = sorted(group.get("device_fingerprint", pd.Series(dtype=str)).astype(str).dropna().unique().tolist())
        rows.append(profile)

    return pd.DataFrame(rows)


def score_against_baseline(event_row: pd.Series, profile_row: pd.Series) -> dict[str, Any]:
    score = 0
    reasons: list[str] = []

    # Category changes - higher weight for security context
    if event_row.get("resource_accessed") not in profile_row.get("allowed_resources", []):
        score += 2  # Increased weight for resource anomalies (insider threat indicator)
        reasons.append("unauthorized resource")
    if event_row.get("geo_location") not in profile_row.get("allowed_locations", []):
        score += 1.5
        reasons.append("impossible travel")
    if event_row.get("auth_method") not in profile_row.get("allowed_auth_methods", []):
        score += 1
        reasons.append("new auth method")
    if event_row.get("device_fingerprint") not in profile_row.get("allowed_devices", []):
        score += 1
        reasons.append("unknown device")

    # Numeric anomalies - tuned for sensitivity
    for column in NUMERIC_COLUMNS:
        mean_value = profile_row.get(f"{column}_mean")
        std_value = profile_row.get(f"{column}_std") or 0.0
        if mean_value is None:
            continue
        event_value = pd.to_numeric(pd.Series([event_row.get(column)]), errors="coerce").fillna(0.0).iloc[0]
        
        # Adaptive tolerance based on variance
        tolerance = max(std_value * 1.5, 1.0)  # Slightly lower tolerance
        deviation = abs(event_value - mean_value)
        
        if deviation > 2.5 * tolerance:
            score += 1.5
            reasons.append(f"{column} high drift")
        elif deviation > 1.5 * tolerance:
            score += 0.5
            reasons.append(f"{column} moderate drift")

    return {
        "baseline_score": score,
        "baseline_reasons": reasons,
        "baseline_flag": score >= 1.5,  # Lowered threshold for better detection
    }


def create_baseline_profile_artifact() -> pd.DataFrame:
    df = pd.read_csv(RAW_DATA_PATH)
    profiles = build_baseline_profiles(df)
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    profiles.to_pickle(PROFILE_PATH)
    return profiles


if __name__ == "__main__":
    profiles = create_baseline_profile_artifact()
    print(profiles.head())
    print(f"Saved baseline profiles: {PROFILE_PATH}")
