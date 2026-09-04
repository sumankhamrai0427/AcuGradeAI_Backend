"""Central application configuration, loaded once from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME = os.getenv("APP_NAME")
    APP_ENV = os.getenv("APP_ENV")
    APP_PORT = int(os.getenv("APP_PORT")) if os.getenv("APP_PORT") else None

    DATABASE_URL = os.getenv("DATABASE_URL")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")) if os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES") else None
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS")) if os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS") else None
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    
    ACTIVE_LLM = os.getenv("ACTIVE_LLM")
    MODEL_NAME = os.getenv("MODEL_NAME")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL")
    MISTRAL_LOCAL_URL = os.getenv("MISTRAL_LOCAL_URL")
    MISTRAL_LOCAL_MODEL = os.getenv("MISTRAL_LOCAL_MODEL")
    MISTRAL_EMBED_MODEL = os.getenv("MISTRAL_EMBED_MODEL")

    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH")

    ARANGO_URL = os.getenv("ARANGO_URL")
    ARANGO_DB = os.getenv("ARANGO_DB")
    ARANGO_USERNAME = os.getenv("ARANGO_USERNAME")
    ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR")
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS").split(",")] if os.getenv("CORS_ORIGINS") else []

    MASTERY_THRESHOLD_DEVELOPING = float(os.getenv("MASTERY_THRESHOLD_DEVELOPING")) if os.getenv("MASTERY_THRESHOLD_DEVELOPING") else None
    MASTERY_THRESHOLD_PROFICIENT = float(os.getenv("MASTERY_THRESHOLD_PROFICIENT")) if os.getenv("MASTERY_THRESHOLD_PROFICIENT") else None
    MASTERY_THRESHOLD_ADVANCED = float(os.getenv("MASTERY_THRESHOLD_ADVANCED")) if os.getenv("MASTERY_THRESHOLD_ADVANCED") else None

config = Config()
