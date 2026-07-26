from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT / "data" / "raw" / "cybersecurity_dataset.csv"
MODEL_PATH = ROOT / "trained_models" / "attack_type_classifier.pkl"
ENCODER_PATH = ROOT / "trained_models" / "attack_type_encoder.pkl"
CATEGORY_ENCODERS_PATH = ROOT / "trained_models" / "attack_type_category_encoders.pkl"
FEATURE_COLUMNS_PATH = ROOT / "trained_models" / "attack_type_feature_columns.pkl"

NUMERIC_COLUMNS = [
    "session_duration",
    "failed_login_attempts",
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

FEATURE_COLUMNS = NUMERIC_COLUMNS + BOOLEAN_COLUMNS + CATEGORICAL_COLUMNS


def _safe_str(value: Any) -> str:
    return str(value).strip() if value is not None else "missing"


def _encode_categorical_row(value: Any, encoder: LabelEncoder) -> int:
    value = _safe_str(value) or "missing"
    if value in encoder.classes_:
        return int(np.where(encoder.classes_ == value)[0][0])
    return -1


def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
    df = df.copy()
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)
        else:
            df[column] = 0.0

    for column in BOOLEAN_COLUMNS:
        if column in df.columns:
            df[column] = df[column].astype(int).fillna(0)
        else:
            df[column] = 0

    encoders: dict[str, LabelEncoder] = {}
    for column in CATEGORICAL_COLUMNS:
        if column in df.columns:
            encoder = LabelEncoder()
            df[column] = encoder.fit_transform(df[column].astype(str).fillna("missing"))
            encoders[column] = encoder
        else:
            df[column] = 0
            encoders[column] = LabelEncoder().fit(["missing"])

    return df[FEATURE_COLUMNS].copy(), encoders


def train_attack_type_classifier(test_size: float = 0.2, random_state: int = 42) -> dict[str, Any]:
    df = pd.read_csv(RAW_DATA_PATH)
    if "attack_type" not in df.columns:
        raise RuntimeError("Raw dataset does not contain attack_type labels")

    attack_rows = df[df["attack_type"].notna()].copy().reset_index(drop=True)
    if attack_rows.empty:
        raise RuntimeError("No labeled attack rows found for attack-type training")

    features, encoders = build_features(attack_rows)
    target_encoder = LabelEncoder()
    labels = target_encoder.fit_transform(attack_rows["attack_type"].astype(str))

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=test_size,
        stratify=labels,
        random_state=random_state,
    )

    model = RandomForestClassifier(n_estimators=200, class_weight="balanced", random_state=random_state)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=target_encoder.classes_, zero_division=0, output_dict=True)

    FEATURE_COLUMNS_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(target_encoder, ENCODER_PATH)
    joblib.dump(encoders, CATEGORY_ENCODERS_PATH)
    joblib.dump(FEATURE_COLUMNS, FEATURE_COLUMNS_PATH)

    return {
        "model_path": str(MODEL_PATH),
        "encoder_path": str(ENCODER_PATH),
        "category_encoders_path": str(CATEGORY_ENCODERS_PATH),
        "feature_columns_path": str(FEATURE_COLUMNS_PATH),
        "classification_report": report,
        "classes": target_encoder.classes_.tolist(),
    }


def load_attack_type_assets() -> tuple[RandomForestClassifier | None, LabelEncoder | None, dict[str, LabelEncoder] | None, list[str] | None]:
    try:
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
        cat_encoders = joblib.load(CATEGORY_ENCODERS_PATH)
        feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
        return model, encoder, cat_encoders, feature_columns
    except Exception:
        return None, None, None, None


def predict_attack_type(event_data: dict[str, Any], model: RandomForestClassifier, encoder: LabelEncoder, cat_encoders: dict[str, LabelEncoder], feature_columns: list[str]) -> str | None:
    if model is None or encoder is None or cat_encoders is None or feature_columns is None:
        return None

    row = {}
    for col in NUMERIC_COLUMNS:
        row[col] = float(event_data.get(col, 0.0) or 0.0)
    for col in BOOLEAN_COLUMNS:
        row[col] = float(bool(event_data.get(col, False)))
    for col in CATEGORICAL_COLUMNS:
        encoder_obj = cat_encoders.get(col)
        if encoder_obj is None:
            row[col] = -1
        else:
            row[col] = _encode_categorical_row(event_data.get(col, ""), encoder_obj)

    X = pd.DataFrame([row], columns=feature_columns)
    try:
        prediction = model.predict(X)[0]
        return str(encoder.inverse_transform([int(prediction)])[0])
    except Exception:
        return None


def load_and_predict(event_data: dict[str, Any]) -> str | None:
    model, encoder, cat_encoders, feature_columns = load_attack_type_assets()
    if model is None:
        return None
    return predict_attack_type(event_data, model, encoder, cat_encoders, feature_columns)
