from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, roc_auc_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.inference import _score_baseline_for_batch, _score_lstm_for_batch, predict

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT / "data" / "raw" / "cybersecurity_dataset.csv"
OUTPUT_PATH = ROOT / "trained_models" / "evaluation_results.json"
TEST_FRACTION = 0.2
ALERT_BUDGET_FRACTION = 0.01


def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "timestamp" not in df.columns:
        raise RuntimeError("Input CSV must include a timestamp column")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def split_time_based(df: pd.DataFrame, test_fraction: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    break_index = int(len(df) * (1.0 - test_fraction))
    return df.iloc[:break_index].reset_index(drop=True), df.iloc[break_index:].reset_index(drop=True)


def compute_alert_budget(df: pd.DataFrame, score_column: str, budget_fraction: float) -> dict[str, Any]:
    if score_column not in df.columns:
        return {
            "alerts_raised": 0,
            "true_positives": 0,
            "false_positives": 0,
            "false_positive_rate_at_budget": None,
            "budget_size": 0,
            "note": f"{score_column} not available"
        }

    budget_size = max(1, int(np.ceil(len(df) * budget_fraction)))
    ranking = df.sort_values([score_column, "timestamp"], ascending=[False, True])
    top_k = ranking.head(budget_size)
    true_positives = int((top_k["label"] == "Attack").sum())
    false_positives = int((top_k["label"] != "Attack").sum())
    false_positive_rate = float(false_positives / budget_size) if budget_size > 0 else 0.0

    return {
        "alerts_raised": int(budget_size),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_positive_rate_at_budget": false_positive_rate,
        "budget_size": int(budget_size),
    }


def safe_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray | None) -> dict[str, Any]:
    metrics = {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "samples_evaluated": int(len(y_true)),
    }
    if y_score is not None and len(np.unique(y_true)) > 1:
        try:
            metrics["auc_roc"] = float(roc_auc_score(y_true, y_score))
        except Exception:
            metrics["auc_roc"] = None
    else:
        metrics["auc_roc"] = None
    return metrics


def build_results(test_df: pd.DataFrame) -> dict[str, Any]:
    baseline_results = _score_baseline_for_batch(test_df)
    baseline_scores = [r["baseline_score"] for r in baseline_results]
    baseline_flags = [r["baseline_flag"] for r in baseline_results]
    baseline_norm = [min(score / 4.0, 1.0) for score in baseline_scores]

    lstm_proba = _score_lstm_for_batch(test_df)
    lstm_available = lstm_proba is not None
    if lstm_available:
        lstm_scores = list(map(float, lstm_proba))
        lstm_flags = [score > 0.5 for score in lstm_scores]
    else:
        lstm_scores = [None] * len(test_df)
        lstm_flags = [False] * len(test_df)

    ensemble_results = predict(test_df)
    ensemble_scores = [float(res.get("risk_score", 0.0)) for res in ensemble_results]
    ensemble_preds = [res.get("status") == "Attack" for res in ensemble_results]

    truth_labels = np.array(test_df["label"].astype(str) == "Attack" , dtype=int)

    baseline_pred = np.array(baseline_flags, dtype=int)
    lstm_pred = np.array(lstm_flags, dtype=int)
    ensemble_pred = np.array(ensemble_preds, dtype=int)

    df = test_df.copy().reset_index(drop=True)
    df["baseline_score"] = baseline_scores
    df["baseline_norm"] = baseline_norm
    df["baseline_pred"] = baseline_pred
    df["lstm_score"] = lstm_scores
    df["lstm_pred"] = lstm_pred
    df["ensemble_score"] = ensemble_scores
    df["ensemble_pred"] = ensemble_pred
    df["true_label"] = truth_labels

    output = {
        "evaluation_timestamp": datetime.utcnow().isoformat() + "Z",
        "dataset": {
            "total_events": int(len(test_df)),
            "attacks": int((df["true_label"] == 1).sum()),
            "attack_rate": float((df["true_label"] == 1).mean()),
            "split": "time-based 80/20"
        },
        "metrics": {
            "baseline": safe_metrics(df["true_label"].to_numpy(), df["baseline_pred"].to_numpy(), df["baseline_norm"].to_numpy()),
            "lstm": safe_metrics(df["true_label"].to_numpy(), df["lstm_pred"].to_numpy(), np.array([s if s is not None else 0.0 for s in df["lstm_score"]], dtype=float) if lstm_available else None),
            "ensemble": safe_metrics(df["true_label"].to_numpy(), df["ensemble_pred"].to_numpy(), df["ensemble_score"].to_numpy()),
        },
        "alert_budget_evaluation": {
            "baseline": compute_alert_budget(df, "baseline_norm", ALERT_BUDGET_FRACTION),
            "lstm": compute_alert_budget(df, "lstm_score", ALERT_BUDGET_FRACTION) if lstm_available else {
                "alerts_raised": 0,
                "true_positives": 0,
                "false_positives": 0,
                "false_positive_rate_at_budget": None,
                "budget_size": int(np.ceil(len(df) * ALERT_BUDGET_FRACTION)),
                "note": "LSTM unavailable in this environment"
            },
            "ensemble": compute_alert_budget(df, "ensemble_score", ALERT_BUDGET_FRACTION),
        },
        "flags": {
            "lstm_available": bool(lstm_available)
        },
    }
    return output


def save_results(results: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def main() -> None:
    print("Loading dataset...")
    df = load_dataset(RAW_DATA_PATH)
    _, test_df = split_time_based(df, TEST_FRACTION)
    print(f"Test split contains {len(test_df)} events")
    results = build_results(test_df)
    save_results(results, OUTPUT_PATH)
    print(f"Saved evaluation results to {OUTPUT_PATH}")
    if not results["flags"]["lstm_available"]:
        print("Warning: LSTM is unavailable in this Python environment. The results file includes baseline and ensemble metrics only.")


if __name__ == "__main__":
    main()
