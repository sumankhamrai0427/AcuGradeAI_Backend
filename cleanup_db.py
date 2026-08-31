"""Development cleanup utility. NEVER destructive by default — every
destructive action requires an explicit flag AND APP_ENV != production.

Usage:
    python cleanup_db.py --tables          # truncate transactional tables (dev only)
    python cleanup_db.py --vector-store    # wipe the local Chroma persistence dir
    python cleanup_db.py --uploads         # delete files in UPLOAD_DIR
    python cleanup_db.py --all             # all of the above
"""
import argparse
import os
import shutil

from sqlalchemy import text

from database.dbConnection import engine
from utils.config import config

# Only these tables are ever truncated — deliberately excludes users/parents/
# students/runbooks/subscription_plans/badges so a dev reset doesn't wipe
# accounts or the curriculum catalog by accident.
TRANSACTIONAL_TABLES = [
    "question_evaluations", "diagnostic_analyses", "exam_submissions",
    "questions", "exams", "messages", "conversations", "shared_dossiers",
    "xp_events", "student_badges", "mastery", "misconceptions",
    "learning_path_nodes", "audit_logs",
]


def _guard_production():
    if config.APP_ENV == "production":
        raise SystemExit("Refusing to run cleanup_db.py against APP_ENV=production.")


def clean_tables():
    _guard_production()
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for table in TRANSACTIONAL_TABLES:
            conn.execute(text(f"TRUNCATE TABLE {table}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    print(f"Truncated: {', '.join(TRANSACTIONAL_TABLES)}")


def clean_vector_store():
    _guard_production()
    path = config.VECTOR_DB_PATH
    if os.path.isdir(path):
        shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)
        print(f"Cleared vector store at {path}")
    else:
        print(f"No vector store directory found at {path}")


def clean_uploads():
    _guard_production()
    path = config.UPLOAD_DIR
    if os.path.isdir(path):
        for name in os.listdir(path):
            if name == ".gitkeep":
                continue
            full = os.path.join(path, name)
            if os.path.isfile(full):
                os.remove(full)
        print(f"Cleared uploaded files in {path}")
    else:
        print(f"No uploads directory found at {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AcuGrade dev database/storage cleanup")
    parser.add_argument("--tables", action="store_true", help="Truncate transactional tables")
    parser.add_argument("--vector-store", action="store_true", help="Wipe local Chroma persistence")
    parser.add_argument("--uploads", action="store_true", help="Delete uploaded files")
    parser.add_argument("--all", action="store_true", help="Run all of the above")
    args = parser.parse_args()

    if not any([args.tables, args.vector_store, args.uploads, args.all]):
        parser.print_help()
        raise SystemExit(0)

    if args.tables or args.all:
        clean_tables()
    if args.vector_store or args.all:
        clean_vector_store()
    if args.uploads or args.all:
        clean_uploads()
