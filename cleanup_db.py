"""Development cleanup utility for AcuGrade AI.
Truncates all transactional tables and user accounts, while automatically re-seeding
the primary Admin user and preserving Master tables (Curriculum, Questions, Roles, Badges, Plans).

Usage:
    python cleanup_db.py                  # Full clean: Truncates transactions & users, auto-seeds Admin
    python cleanup_db.py --tables         # Truncates transactional tables only
    python cleanup_db.py --clean-users    # Truncates user tables & re-seeds Admin
    python cleanup_db.py --vector-store   # Wipes local Chroma vector store
    python cleanup_db.py --uploads        # Deletes files in UPLOAD_DIR
    python cleanup_db.py --all            # Cleans everything (DB, Vector Store, Uploads) + re-seeds Admin
"""
import argparse
import os
import shutil
import sys
from datetime import datetime

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from sqlalchemy import text
from database.dbConnection import get_session
from utils.config import config
from utils.security import hash_password
from model.models import User, Role

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

ADMIN_EMAIL = "admin123@acugrade.ai"
ADMIN_USERNAME = "admin123"
ADMIN_NAME = "Admin123"
ADMIN_PASSWORD_RAW = "admin1234"


def _guard_production():
    if config.APP_ENV == "production":
        raise SystemExit("Refusing to run cleanup_db.py against APP_ENV=production.")


def clean_transactional_tables():
    """Truncates all runtime transactional tables and resets student stats."""
    _guard_production()
    with get_session() as session:
        session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        for table in TRANSACTIONAL_TABLES:
            session.execute(text(f"TRUNCATE TABLE `{table}`;"))
        session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        session.commit()
    print(f"[OK] Truncated {len(TRANSACTIONAL_TABLES)} transactional tables successfully.")


def seed_admin_user(session):
    """Ensures Admin user exists with default credentials."""
    # Find Admin Role ID (default 4)
    admin_role = session.query(Role).filter(Role.role_name == "ADMIN").first()
    admin_role_id = admin_role.id if admin_role else 4

    admin_user = User(
        name=ADMIN_NAME,
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD_RAW),
        role_id=admin_role_id,
        auth_provider="EMAIL",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(admin_user)
    session.flush()
    print(f"[OK] Auto-seeded Admin User:")
    print(f"     * Email:    {ADMIN_EMAIL}")
    print(f"     * Username: {ADMIN_USERNAME}")
    print(f"     * Password: {ADMIN_PASSWORD_RAW}")
    print(f"     * Role ID:  {admin_role_id} (ADMIN)")


def clean_users_and_seed_admin():
    """Truncates student, parent, teacher and users tables, then re-seeds Admin."""
    _guard_production()
    with get_session() as session:
        session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        for table in USER_PROFILE_TABLES:
            session.execute(text(f"TRUNCATE TABLE `{table}`;"))
        session.execute(text("TRUNCATE TABLE `users`;"))
        session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        
        # Seed Admin user
        seed_admin_user(session)
        session.commit()
    print("[OK] User tables truncated and Admin user re-created successfully.")


def clean_all_data_tables():
    """Performs full database cleanup (Transactions + Users) and auto-seeds Admin."""
    _guard_production()
    print("--- Starting Full Database Cleanup ---")
    clean_transactional_tables()
    clean_users_and_seed_admin()
    print("[SUCCESS] All transactional & user data reset. Admin account is ready for login.")


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
    parser = argparse.ArgumentParser(description="AcuGrade Database & Storage Cleanup Utility")
    parser.add_argument("--tables", action="store_true", help="Truncate transactional tables only")
    parser.add_argument("--clean-users", action="store_true", help="Truncate user tables & re-seed Admin")
    parser.add_argument("--all-tables", action="store_true", help="Truncate transaction tables + users & re-seed Admin")
    parser.add_argument("--vector-store", action="store_true", help="Wipe local Chroma vector persistence")
    parser.add_argument("--uploads", action="store_true", help="Delete temporary uploaded files")
    parser.add_argument("--all", action="store_true", help="Run complete reset (DB + Vector Store + Uploads)")
    args = parser.parse_args()

    # Default behavior if executed directly without args: perform full DB clean + Admin re-seed
    if not any([args.tables, args.clean_users, args.all_tables, args.vector_store, args.uploads, args.all]):
        clean_all_data_tables()
        raise SystemExit(0)

    if args.all_tables or args.all:
        clean_all_data_tables()
    elif args.clean_users:
        clean_users_and_seed_admin()
    elif args.tables:
        clean_transactional_tables()

    if args.vector_store or args.all:
        clean_vector_store()
    if args.uploads or args.all:
        clean_uploads()
