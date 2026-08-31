from datetime import datetime

from flask import Blueprint

from database.dbConnection import db_health_check
from database import graph_db, vector_db
from model import mistral_client
from utils.response import success

health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


@health_bp.get("/health")
def health():
    return success({
        "status": "ok",
        "time": datetime.utcnow().isoformat(),
        "database": "up" if db_health_check() else "down",
        "vectorStore": "enabled" if vector_db.is_enabled() else "disabled",
        "knowledgeGraph": "enabled" if graph_db.is_enabled() else "disabled",
        "mistralConfigured": mistral_client.is_configured(),
    })
