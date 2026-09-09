"""Migration script:
1. Creates scheduled_exams and notifications tables if they do not exist.
2. Ensures 'Schedule Exam' page access exists for PARENT role.
"""
from database.dbConnection import get_session, init_db
from model.models import Role, RolePageAccess

def run_migration():
    print("Initializing DB tables...")
    init_db()
    print("Tables verified/created successfully.")

    with get_session() as session:
        # Find Parent role
        parent_role = session.query(Role).filter(Role.role_name.in_(["PARENT", "Parent"])).first()
        if not parent_role:
            print("Parent role not found, creating parent role...")
            parent_role = Role(role_name="PARENT", is_active=True)
            session.add(parent_role)
            session.flush()

        existing_page = session.query(RolePageAccess).filter(
            RolePageAccess.role_id == parent_role.id,
            RolePageAccess.page_route == "/schedule-exam"
        ).first()

        if not existing_page:
            print("Adding 'Schedule Exam' to RolePageAccess for Parent...")
            new_access = RolePageAccess(
                role_id=parent_role.id,
                page_name="Schedule Exam",
                page_route="/schedule-exam",
                icon="CalendarClock",
                menu_order=3,
                is_active=True
            )
            session.add(new_access)
            session.commit()
            print("Added 'Schedule Exam' menu item successfully.")
        else:
            print("'Schedule Exam' menu item already exists.")

if __name__ == "__main__":
    run_migration()
