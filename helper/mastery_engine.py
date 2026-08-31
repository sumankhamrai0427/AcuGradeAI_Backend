"""Student topic mastery tracking (master prompt §19). Upserts per-topic
rows and always increments attempt/correct counters rather than overwriting
history."""
from datetime import datetime

from sqlalchemy.orm import Session

from database import graph_db
from model.models import Mastery
from utils.config import config


def _status_for_score(score: float) -> str:
    if score >= config.MASTERY_THRESHOLD_ADVANCED:
        return "MASTERED"
    if score >= config.MASTERY_THRESHOLD_PROFICIENT:
        return "DEVELOPING"
    if score >= config.MASTERY_THRESHOLD_DEVELOPING:
        return "LEARNING"
    return "CRITICAL_GAP"


def update_mastery_from_insights(session: Session, student_id: str, k_graph_insights: list[dict]):
    """kGraphInsights is the AI's (or fallback's) topic-level assessment for
    this submission: [{topic, masteryPercentage, status, recommendedAction}]."""
    for insight in k_graph_insights:
        topic = insight["topic"]
        new_score = float(insight["masteryPercentage"])

        row = session.query(Mastery).filter(
            Mastery.student_id == student_id, Mastery.topic == topic
        ).one_or_none()

        if row is None:
            row = Mastery(
                student_id=student_id, topic=topic, mastery_score=new_score,
                confidence=new_score, attempt_count=1, correct_count=1 if new_score >= 50 else 0,
                status=_status_for_score(new_score), last_assessed_at=datetime.utcnow(),
            )
            session.add(row)
        else:
            row.mastery_score = max(float(row.mastery_score or 0), new_score)
            row.attempt_count = (row.attempt_count or 0) + 1
            if new_score >= 50:
                row.correct_count = (row.correct_count or 0) + 1
            row.status = _status_for_score(row.mastery_score)
            row.last_assessed_at = datetime.utcnow()

        graph_db.upsert_mastery_edge(student_id, topic, float(row.mastery_score))

    session.flush()


def get_topic_mastery_map(session: Session, student_id: str) -> dict[str, float]:
    rows = session.query(Mastery).filter(Mastery.student_id == student_id).all()
    return {row.topic: float(row.mastery_score) for row in rows}
