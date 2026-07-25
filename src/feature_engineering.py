from pathlib import Path

import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT / "data" / "raw" / "cybersecurity_dataset.csv"
PROCESSED_DATA_PATH = ROOT / "data" / "processed" / "processed_logs.csv"
LABEL_ENCODER_PATH = ROOT / "trained_models" / "label_encoder.pkl"
SCALER_PATH = ROOT / "trained_models" / "scaler.pkl"
FEATURE_COLUMNS_PATH = ROOT / "trained_models" / "feature_columns.pkl"


def build_processed_dataset() -> pd.DataFrame:
    df = pd.read_csv(RAW_DATA_PATH)

    drop_cols = [
        "entity_id", "name", "email", "source_ip", "mac_address",
        "device_fingerprint", "command_sequence", "timestamp", "logout_time",
        "attack_type", "device_id_x", "device_id_y",
        "normal_login_end", "normal_session_duration",
        "normal_entity_type", "normal_department", "normal_geo_location",
        "normal_device_id", "normal_device_fingerprint", "normal_auth_method",
        "normal_resources",
    ]
    df_model = df.drop(columns=[c for c in drop_cols if c in df.columns]).copy()

    bool_cols = [
        "location_changed", "device_changed", "auth_changed",
        "login_time_changed", "long_session", "high_failed_login",
        "resource_changed",
    ]
    df_model[bool_cols] = df_model[bool_cols].astype(int)

    categorical_cols = [
        "geo_location", "resource_accessed", "auth_method",
        "device_type", "operating_system", "browser",
        "department", "office", "entity_type",
    ]

    encoders = {}
    for col in categorical_cols:
        if col in df_model.columns:
            encoder = LabelEncoder()
            df_model[col] = encoder.fit_transform(df_model[col].astype(str))
            encoders[col] = encoder

    numeric_cols = [
        "session_duration", "failed_login_attempts", "login_hour",
        "normal_login_start", "normal_failed_login_attempts", "risk_score",
    ]
    scaler = StandardScaler()
    df_model[numeric_cols] = scaler.fit_transform(df_model[numeric_cols])

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEATURE_COLUMNS_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(encoders, LABEL_ENCODER_PATH)
    joblib.dump(scaler, SCALER_PATH)

    X = df_model.drop(columns=["label"])
    joblib.dump(list(X.columns), FEATURE_COLUMNS_PATH)

    df_model.to_csv(PROCESSED_DATA_PATH, index=False)
    return df_model


if __name__ == "__main__":
    processed = build_processed_dataset()
    print(processed.head())
    print(processed["label"].value_counts())
