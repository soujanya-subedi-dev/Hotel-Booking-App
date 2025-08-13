import os
from datetime import timedelta

class Config:
    # Core
    ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = ENV != "production"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    # Database (PostgreSQL recommended)
    DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
    if not DATABASE_URL:
        # Dev fallback (file DB); use PostgreSQL in production
        DATABASE_URL = "sqlite:////tmp/hotel_app_dev.db"

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,   # 30 min
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
    }

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_EXPIRES_H", "12")))

    # CORS
    # Comma-separated list of allowed origins. Use * for dev only.
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
