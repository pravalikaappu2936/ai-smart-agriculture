import os

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# APPLICATION SETTINGS
# =========================================================

APP_NAME = os.getenv(
    "APP_NAME",
    "AI Smart Agriculture"
)


# =========================================================
# JWT SETTINGS
# =========================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "ai-smart-agriculture-secret-key-change-this-in-production"
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "1440"
    )
)


# =========================================================
# DATABASE SETTINGS
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./smart_agriculture.db"
)


# =========================================================
# WEATHER SETTINGS
# =========================================================

WEATHER_API_KEY = os.getenv(
    "WEATHER_API_KEY",
    ""
)


# =========================================================
# CORS SETTINGS
# =========================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)


# =========================================================
# AI ASSISTANT - OLLAMA SETTINGS
# =========================================================

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b"
)


# =========================================================
# SETTINGS OBJECT
# =========================================================

class Settings:

    # Application
    APP_NAME = APP_NAME

    # JWT
    SECRET_KEY = SECRET_KEY

    ALGORITHM = ALGORITHM

    ACCESS_TOKEN_EXPIRE_MINUTES = (
        ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Database
    DATABASE_URL = DATABASE_URL

    # Weather
    WEATHER_API_KEY = WEATHER_API_KEY

    # Frontend
    FRONTEND_URL = FRONTEND_URL

    # Ollama AI
    OLLAMA_BASE_URL = OLLAMA_BASE_URL

    OLLAMA_MODEL = OLLAMA_MODEL


# =========================================================
# SETTINGS INSTANCE
# =========================================================

settings = Settings()

