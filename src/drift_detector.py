from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.preprocessing import KBinsDiscretizer

ROOT = Path(__file__).resolve().parents[1]


def _distribution_distance(train_values: np.ndarray, test_values: np.ndarray, n_bins: int = 20) -> float:
    train_values = train_values[~np.isnan(train_values)]
    test_values = test_values[~np.isnan(test_values)]

    if len(train_values) == 0 or len(test_values) == 0:
        return 0.0

    estimator = KBinsDiscretizer(n_bins=n_bins, encode="ordinal", strategy="uniform")
    values = np.concatenate([train_values.reshape(-1, 1), test_values.reshape(-1, 1)])
    estimator.fit(values)

    train_binned = estimator.transform(train_values.reshape(-1, 1)).astype(int).flatten()
    test_binned = estimator.transform(test_values.reshape(-1, 1)).astype(int).flatten()

    train_hist, _ = np.histogram(train_binned, bins=n_bins, range=(0, n_bins), density=True)
    test_hist, _ = np.histogram(test_binned, bins=n_bins, range=(0, n_bins), density=True)

    train_hist = train_hist + 1e-9
    test_hist = test_hist + 1e-9

    m = 0.5 * (train_hist + test_hist)
    kl1 = np.sum(train_hist * np.log(train_hist / m))
    kl2 = np.sum(test_hist * np.log(test_hist / m))
    return float(0.5 * (kl1 + kl2))


def feature_drift_scores(train_df: pd.DataFrame, test_df: pd.DataFrame, features: Iterable[str]) -> pd.DataFrame:
    rows = []
    for feature in features:
        if feature not in train_df.columns or feature not in test_df.columns:
            continue
        score = _distribution_distance(train_df[feature].to_numpy(dtype=float), test_df[feature].to_numpy(dtype=float))
        rows.append({"feature": feature, "drift_score": score})
    return pd.DataFrame(rows).sort_values("drift_score", ascending=False).reset_index(drop=True)


def drift_triggered(train_df: pd.DataFrame, test_df: pd.DataFrame, features: Iterable[str], threshold: float = 0.05) -> bool:
    scores = feature_drift_scores(train_df, test_df, features)
    return bool(scores["drift_score"].max() > threshold)
