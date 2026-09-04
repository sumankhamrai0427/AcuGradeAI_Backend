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
        if student_id:
            with get_session() as session:
                result = session.execute(
                    text("""
                        SELECT u.name, s.class_grade, s.target_board 
                        FROM users u 
                        JOIN students s ON u.id = s.id 
                        WHERE u.id = :student_id
                    """),
                    {"student_id": student_id}
                ).mappings().first()
                
                if result:
                    student_context = {
                        "name": result.get("name", "Student"),
                        "classGrade": result.get("class_grade", "Unknown Grade"),
                        "targetBoard": result.get("target_board", "Unknown Board")
                    }

        response_text = generate_chat_response(messages, student_context)

        return jsonify({
            "success": True,
            "response": response_text
        })

    except Exception as e:
        logger.error(f"Chat Controller Error: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Failed to process chat"}), 500
