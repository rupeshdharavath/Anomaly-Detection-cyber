"""
Configuration Settings for Backend
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application Settings"""
    
    # Application
    APP_NAME: str = "Anomaly Detection System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # Data paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data", "raw")
    PROCESSED_DATA_DIR: str = os.path.join(BASE_DIR, "data", "processed")
    MODELS_DIR: str = os.path.join(BASE_DIR, "trained_models")
    
    # Data files
    USERS_CSV: str = os.path.join(DATA_DIR, "users.csv")
    DEVICES_CSV: str = os.path.join(DATA_DIR, "devices.csv")
    PROFILES_CSV: str = os.path.join(DATA_DIR, "user_profiles.csv")
    CYBERSECURITY_CSV: str = os.path.join(DATA_DIR, "cybersecurity_dataset.csv")
    PROCESSED_LOGS_CSV: str = os.path.join(PROCESSED_DATA_DIR, "processed_logs.csv")
    
    # Model files
    LSTM_MODEL: str = os.path.join(MODELS_DIR, "lstm_model.keras")
    BASELINE_PROFILES: str = os.path.join(MODELS_DIR, "baseline_profile.pkl")
    LSTM_THRESHOLD: str = os.path.join(MODELS_DIR, "lstm_threshold.pkl")
    FEATURE_COLUMNS: str = os.path.join(MODELS_DIR, "feature_columns.pkl")
    LSTM_FEATURE_COLUMNS: str = os.path.join(MODELS_DIR, "lstm_feature_columns.pkl")
    SCALER: str = os.path.join(MODELS_DIR, "scaler.pkl")
    EVALUATION_RESULTS: str = os.path.join(MODELS_DIR, "evaluation_results.json")
    
    # Model parameters
    BASELINE_WEIGHT: float = 0.4
    LSTM_WEIGHT: float = 0.6
    ANOMALY_THRESHOLD: float = 0.5
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 500
    
    # Cache (in-memory for now, can be extended to Redis)
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
