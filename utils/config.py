"""Central application configuration, loaded once from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME = os.getenv("APP_NAME", "AcuGrade AI")
    APP_ENV = os.getenv("APP_ENV", "development")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))

    DATABASE_URL = os.getenv(
        "DATABASE_URL", "mysql+pymysql://acugrade:acugrade@localhost:3306/acugrade"
    )

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    MISTRAL_EMBED_MODEL = os.getenv("MISTRAL_EMBED_MODEL", "mistral-embed")

    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_store")

    ARANGO_URL = os.getenv("ARANGO_URL", "")
    ARANGO_DB = os.getenv("ARANGO_DB", "acugrade_graph")
    ARANGO_USERNAME = os.getenv("ARANGO_USERNAME", "")
    ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]

    MASTERY_THRESHOLD_DEVELOPING = float(os.getenv("MASTERY_THRESHOLD_DEVELOPING", "50"))
    MASTERY_THRESHOLD_PROFICIENT = float(os.getenv("MASTERY_THRESHOLD_PROFICIENT", "70"))
    MASTERY_THRESHOLD_ADVANCED = float(os.getenv("MASTERY_THRESHOLD_ADVANCED", "85"))


config = Config()
