from pathlib import Path

import joblib
import pandas as pd

from src.baseline_profiling import score_against_baseline
from src.lstm_sequence_model import build_sequence_windows


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PROFILE_PATH = ROOT / "trained_models" / "baseline_profile.pkl"
LSTM_MODEL_PATH = ROOT / "trained_models" / "lstm_model.keras"
LSTM_THRESHOLD_PATH = ROOT / "trained_models" / "lstm_threshold.pkl"
DATA_PATH = ROOT / "data" / "raw" / "cybersecurity_dataset.csv"


def explain_sample(entity_id: str, sample_index: int = 0) -> dict:
    df = pd.read_csv(DATA_PATH)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    baseline_profiles = pd.read_pickle(BASELINE_PROFILE_PATH)
    entity_rows = df[df["entity_id"] == entity_id].reset_index(drop=True)
    if entity_rows.empty:
        raise ValueError(f"No rows found for entity_id={entity_id}")

    sample = entity_rows.iloc[min(sample_index, len(entity_rows) - 1)]
    sample_df = pd.DataFrame([sample])
    baseline_row = baseline_profiles[baseline_profiles["entity_id"] == entity_id]
    if baseline_row.empty:
        baseline_result = {
            "baseline_score": 0,
            "baseline_reasons": [],
            "baseline_flag": False,
        }
    else:
        baseline_result = score_against_baseline(sample, baseline_row.iloc[0])

    _, _, _, _, metadata = build_sequence_windows(entity_rows, window_size=5)
    if len(entity_rows) > 0:
        sequence_hint = {
            "recent_sequence_length": min(len(entity_rows), metadata.get("window_size", 5)),
            "sequence_available": True,
        }
    else:
        sequence_hint = {
            "recent_sequence_length": 0,
            "sequence_available": False,
        }

    try:
        threshold_info = joblib.load(LSTM_THRESHOLD_PATH)
        lstm_threshold = float(threshold_info.get("threshold", 0.5))
    except Exception:
        lstm_threshold = 0.5

    return {
        "entity_id": entity_id,
        "sample_index": sample_index,
        "baseline_explanation": baseline_result,
        "sequence_hint": sequence_hint,
        "lstm_threshold": lstm_threshold,
        "sample": sample_df.to_dict(orient="records")[0],
    }
