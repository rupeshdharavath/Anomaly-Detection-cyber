from pathlib import Path

from importlib import import_module

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "cybersecurity_dataset.csv"
LSTM_MODEL_PATH = ROOT / "trained_models" / "lstm_model.keras"
LSTM_THRESHOLD_PATH = ROOT / "trained_models" / "lstm_threshold.pkl"


def _annotate_lstm_scores(df: pd.DataFrame) -> pd.DataFrame:
    try:
        keras = import_module('tensorflow.keras')
        from src.lstm_sequence_model import build_sequence_windows
    except Exception:
        annotated = df.copy()
        annotated['lstm_confidence'] = pd.NA
        annotated['lstm_flag'] = pd.NA
        return annotated

    try:
        threshold_info = joblib.load(LSTM_THRESHOLD_PATH)
        threshold = float(threshold_info.get('threshold', 0.5))
        model = keras.models.load_model(LSTM_MODEL_PATH)
    except Exception:
        annotated = df.copy()
        annotated['lstm_confidence'] = pd.NA
        annotated['lstm_flag'] = pd.NA
        return annotated

    sorted_df = df.copy().reset_index().sort_values(['entity_id', 'timestamp']).reset_index(drop=True)
    sequences, _, _, _, _ = build_sequence_windows(sorted_df)
    if len(sequences) != len(sorted_df):
        annotated = df.copy()
        annotated['lstm_confidence'] = pd.NA
        annotated['lstm_flag'] = pd.NA
        return annotated

    lstm_confidence = model.predict(sequences, verbose=0).ravel()
    sorted_df['lstm_confidence'] = lstm_confidence
    sorted_df['lstm_flag'] = sorted_df['lstm_confidence'] >= threshold
    annotated = df.copy()
    annotated['index'] = annotated.index
    annotated = annotated.merge(sorted_df[['index', 'lstm_confidence', 'lstm_flag']], on='index', how='left').drop(columns=['index'])
    return annotated


def build_alert_queue(limit: int = 10) -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = _annotate_lstm_scores(df)
    alerts = df.copy()
    alerts = alerts.sort_values(["risk_score", "session_duration"], ascending=False)
    alerts = alerts.head(limit).copy()
    alerts["alert_rank"] = range(1, len(alerts) + 1)
    alerts["risk_level"] = pd.cut(
        alerts["risk_score"],
        bins=[-1e9, 2, 4, 1e9],
        labels=["Low", "Medium", "High"],
    )
    return alerts[["alert_rank", "entity_id", "label", "risk_score", "risk_level", "resource_accessed", "geo_location", "auth_method", "device_type", "timestamp", "lstm_confidence", "lstm_flag"]]


def print_dashboard(limit: int = 10) -> None:
    alerts = build_alert_queue(limit=limit)
    print("Analyst Alert Queue")
    print(alerts.to_string(index=False))


if __name__ == "__main__":
    print_dashboard()
