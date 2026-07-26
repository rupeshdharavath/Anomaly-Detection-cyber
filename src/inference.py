import joblib
import pandas as pd
from importlib import import_module

from src.baseline_profiling import score_against_baseline
from src.lstm_sequence_model import build_sequence_windows

# Load all models and artifacts once
baseline_profiles = joblib.load('trained_models/baseline_profile.pkl')
try:
    lstm_threshold_info = joblib.load('trained_models/lstm_threshold.pkl')
except FileNotFoundError:
    lstm_threshold_info = {'threshold': 0.5}
LSTM_THRESHOLD = float(lstm_threshold_info['threshold'])


def _score_lstm_for_batch(raw_events: pd.DataFrame):
    try:
        keras = import_module('tensorflow.keras')
    except Exception:
        return None

    try:
        lstm_model = keras.models.load_model('trained_models/lstm_model.keras')
    except Exception:
        return None

    df = raw_events.copy()
    if 'timestamp' not in df.columns:
        return None

    try:
        df = df.sort_values(['entity_id', 'timestamp']).reset_index(drop=True)
        sequences, _, _, _, _ = build_sequence_windows(df)
    except Exception:
        return None

    if len(sequences) == 0:
        return None

    proba = lstm_model.predict(sequences, verbose=0).ravel()
    return proba


def _score_baseline_for_batch(raw_events: pd.DataFrame):
    results = []
    baseline_df = baseline_profiles if isinstance(baseline_profiles, pd.DataFrame) else pd.DataFrame(baseline_profiles)
    for _, row in raw_events.iterrows():
        entity_profile = baseline_df[baseline_df['entity_id'] == row.get('entity_id')]
        if entity_profile.empty:
            results.append({'baseline_flag': False, 'baseline_score': 0, 'baseline_reasons': []})
        else:
            results.append(score_against_baseline(row, entity_profile.iloc[0]))
    return results


def predict(event_features: pd.DataFrame):
    """
    event_features: raw event DataFrame with entity_id/timestamp and event fields.
    Ensemble approach: Baseline profiling + LSTM sequence detection
    """
    if 'timestamp' in event_features.columns:
        event_features = event_features.copy()
        event_features['timestamp'] = pd.to_datetime(event_features['timestamp'], errors='coerce')

    baseline_results = _score_baseline_for_batch(event_features)

    # LSTM sequence detector (optional when enough sequence context exists)
    lstm_proba = None
    lstm_flag = None
    if {'entity_id', 'timestamp', 'label'}.issubset(event_features.columns):
        lstm_proba = _score_lstm_for_batch(event_features)
        if lstm_proba is not None and len(lstm_proba) == len(event_features):
            lstm_flag = lstm_proba >= LSTM_THRESHOLD
        else:
            lstm_flag = None

    # Improved ensemble: Baseline weight 0.4 + LSTM weight 0.6 when both available
    results = []
    for i in range(len(event_features)):
        baseline_score = baseline_results[i]['baseline_score']
        baseline_flag = baseline_results[i]['baseline_flag']
        
        # Calculate confidence based on baseline anomaly score (normalized 0-1)
        baseline_confidence = min(baseline_score / 5.0, 1.0)  # 5 is max reasonable score
        
        # Ensemble decision
        is_attack = baseline_flag
        primary_detector = "Baseline"
        ensemble_confidence = baseline_confidence
        
        if lstm_flag is not None:
            lstm_confidence = float(lstm_proba[i])
            # Both detectors agree - high confidence
            if baseline_flag and lstm_flag[i]:
                is_attack = True
                primary_detector = "Baseline + LSTM"
                ensemble_confidence = (baseline_confidence * 0.4 + lstm_confidence * 0.6)
            # LSTM flags but baseline doesn't - moderate confidence
            elif lstm_flag[i] and not baseline_flag:
                is_attack = lstm_confidence > 0.7
                primary_detector = "LSTM"
                ensemble_confidence = lstm_confidence
        
        if is_attack:
            flagged_sources = [primary_detector]
            result = {
                "status": "Attack",
                "attack_type": "Anomalous",
                "flagged_by": primary_detector,
                "confidence": float(ensemble_confidence),
                "risk_score": float(ensemble_confidence),
                "baseline_score": baseline_score,
                "baseline_reasons": baseline_results[i]['baseline_reasons']
            }
            if lstm_flag is not None:
                result["lstm_confidence"] = float(lstm_proba[i])
            results.append(result)
        else:
            results.append({
                "status": "Normal",
                "baseline_score": baseline_score,
                "confidence": 1.0 - float(ensemble_confidence),
                "risk_score": float(ensemble_confidence)
            })

    return results