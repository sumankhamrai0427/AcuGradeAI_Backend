from flask import jsonify, request, g
from sqlalchemy import text

from middleware.authMiddleware import token_required
from helper.chat_engine import generate_chat_response
from database.dbConnection import get_session
from utils.logger import logger

@token_required
def chat():
    """
    POST /api/v1/chat
    Request Body:
    {
      "messages": [{"role": "user", "content": "..."}],
      "student_id": "optional_id"
    }
    """
    try:
        user_id = g.current_user_id
        if not user_id:
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        data = request.json or {}
        messages = data.get("messages", [])
        student_id = data.get("student_id")

        if not messages:
            return jsonify({"success": False, "message": "No messages provided"}), 400

        student_context = None
        target_student_id = student_id
        
        with get_session() as session:
            if not target_student_id:
                # Check if current user is a student
                is_student = session.execute(
                    text("SELECT id FROM students WHERE id = :uid"),
                    {"uid": user_id}
                ).scalar()
                if is_student:
                    target_student_id = user_id

            if target_student_id:
                result = session.execute(
                    text("""
                        SELECT u.name, s.class_grade, s.target_board, s.average_score
                        FROM users u 
                        JOIN students s ON u.id = s.id 
                        WHERE u.id = :student_id
                    """),
                    {"student_id": target_student_id}
                ).mappings().first()
                
                if result:
                    # Query weak topics (mastery < 75%)
                    weak_rows = session.execute(
                        text("""
                            SELECT topic FROM mastery 
                            WHERE student_id = :student_id AND mastery_score < 75
                            ORDER BY mastery_score ASC LIMIT 5
                        """),
                        {"student_id": target_student_id}
                    ).fetchall()
                    weak_topics = [r[0] for r in weak_rows]

                    # Query recent 3 exam marks
                    recent_subs = session.execute(
                        text("""
                            SELECT marks_obtained FROM exam_submissions 
                            WHERE student_id = :student_id
                            ORDER BY submitted_at DESC LIMIT 3
                        """),
                        {"student_id": target_student_id}
                    ).fetchall()
                    recent_scores = [r[0] for r in recent_subs]

                    student_context = {
                        "name": result.get("name", "Student"),
                        "classGrade": result.get("class_grade", "Class 10"),
                        "targetBoard": result.get("target_board", "CBSE"),
                        "averageScore": float(result.get("average_score", 0)) if result.get("average_score") is not None else 0,
                        "weakTopics": weak_topics,
                        "recentScores": recent_scores
                    }

        response_text = generate_chat_response(messages, student_context)

        return jsonify({
            "success": True,
            "response": response_text
        })

    except Exception as e:
        logger.error(f"Chat Controller Error: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Failed to process chat"}), 500
