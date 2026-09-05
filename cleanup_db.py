"""Development cleanup utility.
Preserves Master tables, Curriculum, Question Banks, Roles and Admin Account.

Usage:
    python cleanup_db.py --tables          # truncate transactional tables & reset student stats
    python cleanup_db.py --clean-users     # truncate non-admin users (preserves Admin user & masters)
    python cleanup_db.py --all-tables      # truncate all data tables except Admin and master tables
    python cleanup_db.py --vector-store    # wipe the local Chroma persistence dir
    python cleanup_db.py --uploads         # delete files in UPLOAD_DIR
    python cleanup_db.py --all             # clean transactions, non-admin users, vector-store & uploads
"""
import argparse
import os
import shutil
import sys

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from sqlalchemy import text
from database.dbConnection import get_session
from utils.config import config

# 1. Transactional data tables
TRANSACTIONAL_TABLES = [
    "question_evaluations", "diagnostic_analyses", "exam_submissions",
    "questions", "exams", "messages", "conversations", "ptm_schedules",
    "shared_dossiers", "xp_events", "student_badges", "mastery",
    "misconceptions", "learning_path_nodes", "audit_logs",
    "refresh_tokens", "document_chunks", "documents"
]

# 2. User profile extension tables
USER_PROFILE_TABLES = ["students", "parents", "teachers"]


def _guard_production():
    if config.APP_ENV == "production":
        raise SystemExit("Refusing to run cleanup_db.py against APP_ENV=production.")


def clean_transactional_tables():
    _guard_production()
    with get_session() as session:
        session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        for table in TRANSACTIONAL_TABLES:
            session.execute(text(f"TRUNCATE TABLE `{table}`;"))
        session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        
        # Reset student stats if students table exists
        try:
            session.execute(text("""
                UPDATE students SET 
                    daily_exams_taken_today = 0,
                    total_exams_taken = 0,
                    average_score = 0.00,
                    streak_days = 0,
                    xp = 250,
                    level = 1;
            """))
        except Exception:
            pass
        session.commit()
    print(f"[OK] Truncated transactional tables & reset metrics: {', '.join(TRANSACTIONAL_TABLES)}")


def clean_non_admin_users():
    _guard_production()
    with get_session() as session:
        session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        for table in USER_PROFILE_TABLES:
            session.execute(text(f"TRUNCATE TABLE `{table}`;"))
        session.execute(text("DELETE FROM users WHERE role_id != 4;"))
        session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        session.commit()
    print("[OK] Deleted non-admin users. Only Admin (role_id=4) & master data preserved.")


def clean_all_data_tables():
    _guard_production()
    clean_transactional_tables()
    clean_non_admin_users()
    print("[OK] All transaction data and test users cleaned successfully (Admin preserved).")


def clean_vector_store():
    _guard_production()
    path = config.VECTOR_DB_PATH
    if os.path.isdir(path):
        shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)
        print(f"[OK] Cleared vector store at {path}")
    else:
        print(f"[i] No vector store directory found at {path}")


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
        print(f"[OK] Cleared uploaded files in {path}")
    else:
        print(f"[i] No uploads directory found at {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AcuGrade dev database/storage cleanup")
    parser.add_argument("--tables", action="store_true", help="Truncate transactional tables only")
    parser.add_argument("--clean-users", action="store_true", help="Delete non-admin users (preserve Admin)")
    parser.add_argument("--all-tables", action="store_true", help="Truncate transaction tables and test users")
    parser.add_argument("--vector-store", action="store_true", help="Wipe local Chroma persistence")
    parser.add_argument("--uploads", action="store_true", help="Delete uploaded files")
    parser.add_argument("--all", action="store_true", help="Run all cleanup tasks")
    args = parser.parse_args()

    if not any([args.tables, args.clean_users, args.all_tables, args.vector_store, args.uploads, args.all]):
        # Default behavior if executed directly: clean transactions
        clean_transactional_tables()
        raise SystemExit(0)

    if args.all_tables or args.all:
        clean_all_data_tables()
    elif args.clean_users:
        clean_non_admin_users()
    elif args.tables:
        clean_transactional_tables()

    if args.vector_store or args.all:
        clean_vector_store()
    if args.uploads or args.all:
        clean_uploads()
