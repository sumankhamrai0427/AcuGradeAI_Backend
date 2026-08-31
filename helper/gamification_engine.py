"""XP, badges, and leaderboard. Ported from the frontend's original
App.tsx `handleExamComplete` / `handleAwardXP` — the key difference is that
here it runs server-side against persisted data, so the client can no longer
compute its own XP (master prompt §23, and see docs/FRONTEND_BACKEND_MAPPING.md
§2.5 for why the original client-side version was unsafe to trust)."""
import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from model.models import Student, Badge, StudentBadge, XPEvent
from utils.constants import BADGE_IDS


def compute_exam_xp(marks_obtained: int, time_taken_seconds: int) -> int:
    base_xp = marks_obtained * 10
    perfect_bonus = 50 if marks_obtained == 10 else 0
    speed_bonus = 25 if time_taken_seconds < 360 else 0
    streak_bonus = 30
    return base_xp + perfect_bonus + speed_bonus + streak_bonus


def award_xp(session: Session, student: Student, amount: int, reason: str) -> Student:
    student.xp = (student.xp or 250) + amount
    student.level = (student.xp // 250) + 1
    session.add(XPEvent(id=str(uuid.uuid4()), student_id=student.id, amount=amount, reason=reason))
    session.flush()
    return student


def evaluate_badge_unlocks(
    session: Session,
    student: Student,
    marks_obtained: int,
    time_taken_seconds: int,
    difficulty: str,
) -> list[str]:
    """Returns newly-unlocked badge ids (empty if none). Ported unlock rules
    from App.tsx's `handleExamComplete`."""
    existing_ids = {
        row.badge_id
        for row in session.query(StudentBadge).filter(StudentBadge.student_id == student.id).all()
    }

    to_unlock = {BADGE_IDS["PIONEER"]}
    if marks_obtained == 10:
        to_unlock.add(BADGE_IDS["PERFECT_10"])
    if time_taken_seconds < 360 and marks_obtained >= 8:
        to_unlock.add(BADGE_IDS["SPEED_DEMON"])
    if (student.streak_days or 0) + 1 >= 3:
        to_unlock.add(BADGE_IDS["STREAK_3"])
    if (student.streak_days or 0) + 1 >= 7:
        to_unlock.add(BADGE_IDS["STREAK_7"])
    if difficulty == "hard" and marks_obtained >= 9:
        to_unlock.add(BADGE_IDS["OLYMPIAD_THINKER"])

    newly_unlocked = [bid for bid in to_unlock if bid not in existing_ids]

    for badge_id in newly_unlocked:
        badge = session.get(Badge, badge_id)
        if badge is None:
            continue  # badge not seeded — skip rather than fail the whole submission
        session.add(StudentBadge(student_id=student.id, badge_id=badge_id, unlocked_at=datetime.utcnow()))
        if badge.xp_reward:
            award_xp(session, student, badge.xp_reward, f"badge:{badge_id}")

    session.flush()
    return newly_unlocked


def get_leaderboard(session: Session, period: str = "all_time", limit: int = 50) -> list[dict]:
    """period: daily | weekly | monthly | all_time. For non-all_time periods,
    ranks by XP earned within the window (from xp_events); all_time ranks by
    the student's running total."""
    students = session.query(Student).all()

    if period == "all_time":
        scored = [(s, s.xp or 0) for s in students]
    else:
        window_days = {"daily": 1, "weekly": 7, "monthly": 30}.get(period, 3650)
        since = datetime.utcnow() - timedelta(days=window_days)
        scored = []
        for s in students:
            window_xp = (
                session.query(XPEvent)
                .filter(XPEvent.student_id == s.id, XPEvent.created_at >= since)
                .all()
            )
            scored.append((s, sum(e.amount for e in window_xp)))

    scored.sort(key=lambda pair: pair[1], reverse=True)

    leaderboard = []
    for rank, (student, points) in enumerate(scored[:limit], start=1):
        badge_count = session.query(StudentBadge).filter(StudentBadge.student_id == student.id).count()
        leaderboard.append(
            {
                "rank": rank,
                "studentId": student.id,
                "studentName": student.user.name if student.user else "Student",
                "avatar": student.avatar,
                "classGrade": student.class_grade,
                "targetBoard": student.target_board,
                "schoolName": student.school_name,
                "xp": points,
                "level": student.level,
                "averageScore": float(student.average_score or 0),
                "examsCompleted": student.total_exams_taken,
                "streakDays": student.streak_days,
                "badgesCount": badge_count,
            }
        )
    return leaderboard
