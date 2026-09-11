from utils.date_helper import now_ist
from datetime import date

from flask import g
from flask import g, request
from sqlalchemy import exists, or_
from sqlalchemy.orm import aliased, joinedload

from database.dbConnection import get_session
from middleware.authMiddleware import token_required
from middleware.roleMiddleware import roles_required
from model.models import User, Student, Exam, ExamSubmission, Runbook, Role
from utils.constants import BOARDS, CLASS_GRADES
from utils.errors import NotFoundError
from utils.pagination import get_pagination_params, paginated_response
from utils.response import success
from utils.serializers import student_to_child_account


def statistics():
    """Public — matches the frontend's original unauthenticated GET /api/stats
    used by SuperAdminPanel's analytics tab and homepage counters."""
    with get_session() as session:
        total_generated = session.query(Exam).count()
        total_completed = session.query(ExamSubmission).count()
        total_runbooks = session.query(Runbook).filter(Runbook.status == "PUBLISHED").count()

        avg_row = session.query(ExamSubmission.accuracy_percentage).all()
        avg_score = (
            round(sum(float(r[0]) for r in avg_row) / len(avg_row) / 10, 2) if avg_row else 0
        )  # convert 0-100% back to an out-of-10 average, matching the frontend's displayed metric

        return success({
            "totalExamsGenerated": total_generated,
            "totalExamsCompleted": total_completed,
            "totalRunbooks": total_runbooks,
            "supportedBoards": BOARDS,
            "supportedGrades": CLASS_GRADES,
            "averagePlatformScore": avg_score,
        })


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def admin_dashboard():
    from datetime import datetime, timedelta

    with get_session() as session:
        total_users = session.query(User).count()
        total_students = session.query(Student).count()
        total_exams = session.query(Exam).count()
        total_submissions = session.query(ExamSubmission).count()
        total_runbooks = session.query(Runbook).count()

        avg_row = session.query(ExamSubmission.accuracy_percentage).all()
        avg_score = (
            round(sum(float(r[0]) for r in avg_row) / len(avg_row), 1) if avg_row else 0.0
        )

        # ── 1. Weekly Assessment Activity (Mon -> Sun) ──
        today = now_ist().date()
        start_of_week = today - timedelta(days=today.weekday())
        days_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekly_activity = []
        for i, day_name in enumerate(days_map):
            day_date = start_of_week + timedelta(days=i)
            day_start = datetime.combine(day_date, datetime.min.time())
            day_end = datetime.combine(day_date, datetime.max.time())

            gen_count = session.query(Exam).filter(Exam.created_at >= day_start, Exam.created_at <= day_end).count()
            sub_count = session.query(ExamSubmission).filter(ExamSubmission.submitted_at >= day_start, ExamSubmission.submitted_at <= day_end).count()

            weekly_activity.append({
                "day": day_name,
                "date": day_date.strftime("%b %d"),
                "generated": gen_count,
                "completed": sub_count,
            })

        # ── 2. Subject Performance Breakdown ──
        subjects_data = {}
        exams = session.query(Exam.id, Exam.subject).all()
        exam_subject_map = {e[0]: (e[1] or "General").strip().title() for e in exams}

        for e_id, subj in exam_subject_map.items():
            if subj not in subjects_data:
                subjects_data[subj] = {"subject": subj, "examsGenerated": 0, "submissions": 0, "totalAccuracy": 0.0}
            subjects_data[subj]["examsGenerated"] += 1

        submissions = session.query(ExamSubmission.exam_id, ExamSubmission.accuracy_percentage).all()
        for sub_exam_id, acc in submissions:
            subj = exam_subject_map.get(sub_exam_id, "General")
            if subj not in subjects_data:
                subjects_data[subj] = {"subject": subj, "examsGenerated": 0, "submissions": 0, "totalAccuracy": 0.0}
            subjects_data[subj]["submissions"] += 1
            subjects_data[subj]["totalAccuracy"] += float(acc or 0)

        subject_list = []
        for subj, item in subjects_data.items():
            avg_subj_acc = round(item["totalAccuracy"] / item["submissions"], 1) if item["submissions"] > 0 else 0.0
            subject_list.append({
                "subject": subj,
                "examsCount": item["examsGenerated"],
                "submissionsCount": item["submissions"],
                "averageAccuracy": avg_subj_acc,
            })
        subject_list.sort(key=lambda x: x["examsCount"], reverse=True)

        return success({
            "totalUsers": total_users,
            "totalStudents": total_students,
            "totalExamsGenerated": total_exams,
            "totalExamsCompleted": total_submissions,
            "totalRunbooks": total_runbooks,
            "averagePlatformScore": avg_score,
            "weeklyActivity": weekly_activity,
            "subjectBreakdown": subject_list[:6],
        })


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def list_users():
    page, limit, offset = get_pagination_params()
    with get_session() as session:
        total = session.query(User).count()
        users = session.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()
        search = request.args.get("search", "").strip()
        query = session.query(User).outerjoin(Role)
        if search:
            search_pattern = f"%{search}%"
            student_user = aliased(User)
            student_role = aliased(Role)
            matching_child = exists().where(
                Student.parent_id == User.id,
                Student.id == student_user.id,
                student_user.role_id == student_role.id,
                or_(
                    student_user.name.ilike(search_pattern),
                    student_user.email.ilike(search_pattern),
                    student_role.role_name.ilike(search_pattern),
                ),
            )
            query = query.filter(or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern),
                Role.role_name.ilike(search_pattern),
                matching_child,
            ))

        # Build the complete parent-child relationship before paginating top-level
        # rows. Student users are represented under their parent rather than as
        # duplicate standalone rows.
        all_users = query.order_by(User.created_at.desc()).all()
        students = session.query(Student).options(joinedload(Student.user)).order_by(
            Student.created_at.asc(), Student.id.asc()
        ).all()

        linked_students = {}
        student_user_ids = set()
        for student in students:
            if not student.user or student.id in student_user_ids:
                continue
            student_user_ids.add(student.id)
            linked_students.setdefault(student.parent_id, []).append({
                "id": student.id,
                "name": student.user.name or student.user.username or "Student",
            })

        grouped_users = [user for user in all_users if user.id not in student_user_ids]
        total = len(grouped_users)
        users = grouped_users[offset:offset + limit]

        items = [
            {
                "id": u.id,
                "name": u.name or u.username or "User",
                "username": u.username,
                "email": u.email or "—",
                "role": (u.role.role_name if u.role else "User").title(),
                "roleName": (u.role.role_name if u.role else "USER").upper(),
                "isActive": bool(u.is_active),
                "status": "Active" if u.is_active else "Inactive",
                "createdAt": u.created_at.isoformat() if u.created_at else None,
                "linkedStudents": linked_students.get(u.id, []) if u.role and u.role.role_name.upper() == "PARENT" else None,
            }
            for u in users
        ]
        return success(paginated_response(items, total, page, limit))


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def update_user(user_id):
    payload = request.get_json(silent=True) or {}
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise NotFoundError("User not found")

        if "name" in payload:
            user.name = str(payload["name"]).strip()
        if "email" in payload:
            user.email = str(payload["email"]).strip()
        if "role" in payload:
            role = session.query(Role).filter(Role.role_name == str(payload["role"]).upper()).first()
            if not role:
                raise NotFoundError("Role not found")
            user.role = role

        session.commit()
        return success({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.role_name.title() if user.role else "User",
            "roleName": user.role.role_name.upper() if user.role else "USER",
        })


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def delete_user(user_id):
    with get_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise NotFoundError("User not found")
        session.delete(user)
        session.commit()
        return success({"deleted": True, "id": user_id})


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def list_students():
    page, limit, offset = get_pagination_params()
    with get_session() as session:
        total = session.query(Student).count()
        students = session.query(Student).order_by(Student.created_at.desc()).offset(offset).limit(limit).all()
        items = [student_to_child_account(s) for s in students]
        return success(paginated_response(items, total, page, limit))


@token_required
@roles_required("ADMIN", "SUPER_ADMIN", "PARENT")
def reset_quota(student_id):
    with get_session() as session:
        student = session.get(Student, student_id)
        if not student:
            raise NotFoundError("Student not found")
        if g.current_user_role == "PARENT" and student.parent_id != g.current_user_id:
            raise NotFoundError("Student not found")
        student.daily_exams_taken_today = 0
        student.last_exam_date = date.today()
        return success({"reset": True})


@token_required
@roles_required("ADMIN", "SUPER_ADMIN")
def list_audit_logs():
    """Fetches paginated audit logs with optional filtering by action, user_id, or entity_type."""
    from flask import request
    from model.models import AuditLog

    page, limit, offset = get_pagination_params()
    action_filter = request.args.get("action")
    entity_filter = request.args.get("entityType") or request.args.get("entity_type")
    user_id_filter = request.args.get("userId") or request.args.get("user_id")

    with get_session() as session:
        query = session.query(AuditLog)
        if action_filter:
            query = query.filter(AuditLog.action.ilike(f"%{action_filter.strip()}%"))
        if entity_filter:
            query = query.filter(AuditLog.entity_type == entity_filter.strip().upper())
        if user_id_filter and str(user_id_filter).isdigit():
            query = query.filter(AuditLog.user_id == int(user_id_filter))

        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

        user_ids = {log.user_id for log in logs if log.user_id}
        user_map = {}
        if user_ids:
            users = session.query(User).filter(User.id.in_(user_ids)).all()
            user_map = {u.id: {"name": u.name, "username": u.username, "email": u.email} for u in users}

        items = [
            {
                "id": log.id,
                "userId": log.user_id,
                "userName": user_map.get(log.user_id, {}).get("name") if log.user_id else None,
                "userEmail": user_map.get(log.user_id, {}).get("email") if log.user_id else None,
                "action": log.action,
                "entityType": log.entity_type,
                "entityId": log.entity_id,
                "ipAddress": log.ip_address,
                "createdAt": f"{log.created_at.isoformat()}+05:30" if log.created_at else None,
                "createdAtFormatted": log.created_at.strftime("%d %b %Y, %I:%M:%S %p IST") if log.created_at else None,
            }
            for log in logs
        ]
        return success(paginated_response(items, total, page, limit))


