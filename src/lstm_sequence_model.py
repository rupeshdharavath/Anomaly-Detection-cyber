from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score
from sklearn.utils.class_weight import compute_class_weight

try:
    from tensorflow import keras
    from tensorflow.keras import layers
except Exception as exc:  # pragma: no cover - import guard for environments without TensorFlow
    keras = None
    layers = None
    TF_IMPORT_ERROR = exc
else:
    TF_IMPORT_ERROR = None


ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT / "data" / "raw" / "cybersecurity_dataset.csv"
MODEL_PATH = ROOT / "trained_models" / "lstm_model.keras"
FEATURE_PATH = ROOT / "trained_models" / "lstm_feature_columns.pkl"
METADATA_PATH = ROOT / "trained_models" / "lstm_metadata.pkl"
THRESHOLD_PATH = ROOT / "trained_models" / "lstm_threshold.pkl"

WINDOW_SIZE = 5
RANDOM_STATE = 42
EPOCHS = 15  # Increased for better convergence
BATCH_SIZE = 32  # Reduced for better gradient updates
VALIDATION_SPLIT = 0.2  # Increased validation set

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


def load_raw_sequence_data() -> pd.DataFrame:
    df = pd.read_csv(RAW_DATA_PATH)
    if "timestamp" not in df.columns:
        raise ValueError("cybersecurity_dataset.csv must contain a timestamp column")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values(["entity_id", "timestamp"]).reset_index(drop=True)
    return df


def build_event_feature_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    working = df.copy()
    for column in BOOLEAN_COLUMNS:
        if column in working.columns:
            working[column] = working[column].fillna(0).astype(int)
    for column in NUMERIC_COLUMNS:
        if column in working.columns:
            working[column] = pd.to_numeric(working[column], errors="coerce").fillna(0.0)

    numeric_frame = working[[column for column in NUMERIC_COLUMNS + BOOLEAN_COLUMNS if column in working.columns]].copy()
    categorical_source = working[[column for column in CATEGORICAL_COLUMNS if column in working.columns]].astype(str)
    categorical_frame = pd.get_dummies(categorical_source, columns=categorical_source.columns.tolist(), prefix=categorical_source.columns.tolist())

    feature_frame = pd.concat([numeric_frame.reset_index(drop=True), categorical_frame.reset_index(drop=True)], axis=1)
    feature_columns = list(feature_frame.columns)
    numeric_feature_columns = list(numeric_frame.columns)
    return feature_frame, feature_columns, numeric_feature_columns


def build_sequence_windows(
    df: pd.DataFrame,
    window_size: int = WINDOW_SIZE,
) -> tuple[np.ndarray, np.ndarray, list[str], list[str], dict[str, Any]]:
    feature_frame, feature_columns, numeric_feature_columns = build_event_feature_frame(df)
    feature_matrix = feature_frame.to_numpy(dtype=np.float32)
    labels = (df["label"].astype(str) == "Attack").astype(np.int32).to_numpy()
    entity_ids = df["entity_id"].astype(str).to_numpy()
    timestamps = df["timestamp"].to_numpy()

    sequences: list[np.ndarray] = []
    targets: list[int] = []
    sequence_entities: list[str] = []
    sequence_timestamps: list[Any] = []

    for entity_id in pd.unique(entity_ids):
        entity_mask = entity_ids == entity_id
        entity_indices = np.where(entity_mask)[0]
        for end_position, row_index in enumerate(entity_indices):
            start_position = max(0, end_position - window_size + 1)
            window_indices = entity_indices[start_position : end_position + 1]
            window = feature_matrix[window_indices]
            if len(window) < window_size:
                padding = np.zeros((window_size - len(window), feature_matrix.shape[1]), dtype=np.float32)
                window = np.vstack([padding, window])
            sequences.append(window)
            targets.append(int(labels[row_index]))
            sequence_entities.append(str(entity_id))
            sequence_timestamps.append(timestamps[row_index])

    metadata = {
        "window_size": window_size,
        "sequence_entities": sequence_entities,
        "sequence_timestamps": sequence_timestamps,
        "numeric_feature_columns": numeric_feature_columns,
    }
    return np.asarray(sequences, dtype=np.float32), np.asarray(targets, dtype=np.int32), feature_columns, numeric_feature_columns, metadata


def build_lstm_model(input_shape: tuple[int, int]) -> keras.Model:
    if keras is None or layers is None:
        raise ImportError(
            "TensorFlow is not available in this environment. Install TensorFlow in Python 3.12 before training the LSTM model."
        ) from TF_IMPORT_ERROR

    model = keras.Sequential(
        [
            layers.Input(shape=input_shape),
            layers.Masking(mask_value=0.0),
            layers.LSTM(128, return_sequences=True),  # Larger LSTM + return sequences for deep learning
            layers.Dropout(0.4),
            layers.LSTM(64, return_sequences=False),   # Second LSTM layer for better pattern recognition
            layers.Dropout(0.3),
            layers.Dense(64, activation="relu"),      # Larger dense layer
            layers.Dropout(0.3),
            layers.Dense(32, activation="relu"),      # Additional dense layer for better feature extraction
            layers.Dropout(0.2),
            layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc"), keras.metrics.Precision(name="precision"), keras.metrics.Recall(name="recall")],
    )
    return model


def scale_numeric_channels(
    train_sequences: np.ndarray,
    test_sequences: np.ndarray,
    numeric_feature_count: int,
) -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    scaler = StandardScaler()
    train_flat = train_sequences.reshape(-1, train_sequences.shape[-1])
    test_flat = test_sequences.reshape(-1, test_sequences.shape[-1])

    scaler.fit(train_flat[:, :numeric_feature_count])
    train_flat[:, :numeric_feature_count] = scaler.transform(train_flat[:, :numeric_feature_count])
    test_flat[:, :numeric_feature_count] = scaler.transform(test_flat[:, :numeric_feature_count])

    return (
        train_flat.reshape(train_sequences.shape),
        test_flat.reshape(test_sequences.shape),
        scaler,
    )


def train_lstm_sequence_model(
    window_size: int = WINDOW_SIZE,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
) -> dict[str, Any]:
    df = load_raw_sequence_data()
    sequences, targets, feature_columns, numeric_feature_columns, metadata = build_sequence_windows(df, window_size=window_size)

    X_train, X_test, y_train, y_test = train_test_split(
        sequences,
        targets,
        test_size=0.2,
        stratify=targets,
        random_state=RANDOM_STATE,
    )

    numeric_feature_count = len(numeric_feature_columns)
    X_train, X_test, scaler = scale_numeric_channels(X_train, X_test, numeric_feature_count)

    class_labels = np.unique(y_train)
    class_weights = compute_class_weight(class_weight="balanced", classes=class_labels, y=y_train)
    class_weight_mapping = {int(label): float(weight) for label, weight in zip(class_labels, class_weights)}

    model = build_lstm_model((window_size, sequences.shape[-1]))
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_auc",
            mode="max",
            patience=3,
            restore_best_weights=True,
        )
    ]

    history = model.fit(
        X_train,
        y_train,
        validation_split=VALIDATION_SPLIT,
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight_mapping,
        callbacks=callbacks,
        verbose=1,
    )

    y_proba = model.predict(X_test, verbose=0).ravel()
    threshold_info = calibrate_threshold(y_test, y_proba)
    y_pred = (y_proba >= threshold_info["threshold"]).astype(int)

    results = {
        "classification_report": classification_report(y_test, y_pred, digits=4),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "history": history.history,
        "feature_columns": feature_columns,
        "numeric_feature_columns": numeric_feature_columns,
        "class_weight": class_weight_mapping,
        "scaler": scaler,
        "model": model,
        "X_test": X_test,
        "y_test": y_test,
        "y_proba": y_proba,
        "y_pred": y_pred,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH)
    joblib.dump(feature_columns, FEATURE_PATH)
    joblib.dump(
        {
            "window_size": window_size,
            "numeric_feature_count": numeric_feature_count,
            "numeric_feature_columns": numeric_feature_columns,
            "class_weight": class_weight_mapping,
            "scaler": scaler,
        },
        METADATA_PATH,
    )
    joblib.dump(threshold_info, THRESHOLD_PATH)

    results["threshold_info"] = threshold_info
    return results


def calibrate_threshold(y_true: np.ndarray, y_proba: np.ndarray) -> dict[str, float]:
    thresholds = np.arange(0.1, 0.91, 0.05)
    best_threshold = 0.5
    best_f1 = -1.0
    best_precision = 0.0
    best_recall = 0.0

    for threshold in thresholds:
        y_pred = (y_proba >= threshold).astype(int)
        precision = float(precision_score(y_true, y_pred, zero_division=0))
        recall = float(recall_score(y_true, y_pred, zero_division=0))
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = float(2 * precision * recall / (precision + recall))

        if f1 > best_f1:
            best_threshold = float(threshold)
            best_f1 = f1
            best_precision = precision
            best_recall = recall

    return {
        "threshold": best_threshold,
        "f1": best_f1,
        "precision": best_precision,
        "recall": best_recall,
    }


if __name__ == "__main__":
    output = train_lstm_sequence_model()
    print(output["classification_report"])
    print(output["confusion_matrix"])
    print(output["roc_auc"])
