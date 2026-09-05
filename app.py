"""AcuGrade AI backend entry point.

app.py defines all API route endpoints explicitly with @app.route
and delegates execution directly to their respective controller functions.
"""
import time

from flask import Flask, g, request
from flask_cors import CORS

from controller import (
    admin_controller,
    auth_controller,
    communication_controller,
    exam_controller,
    gamification_controller,
    health_controller,
    leaderboard_controller,
    parent_controller,
    runbook_controller,
    student_controller,
    teacher_controller,
    upload_file_controller,
    chat_controller,
)
from middleware.dbContext import register_db_teardown
from middleware.errorMiddleware import register_error_handlers
from middleware.rateLimitMiddleware import rate_limit
from utils.config import config
from utils.logger import log_request


def create_app() -> Flask:
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)

    register_error_handlers(app)
    register_db_teardown(app)

    # ------------------------------------------------------------
    # Request Hooks
    # ------------------------------------------------------------
    @app.before_request
    def _before():
        g._start_time = time.time()
        if request.path != "/api/v1/health":
            rate_limit()

    @app.after_request
    def _after(response):
        duration_ms = (time.time() - getattr(g, "_start_time", time.time())) * 1000
        log_request(
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            getattr(g, "current_user_id", None),
        )
        # Secure headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    # ============================================================
    # 1. Health Endpoints
    # ============================================================
    @app.route("/api/v1/health", methods=["GET"])
    def api_health():
        return health_controller.health()

    # ============================================================
    # 2. Authentication & Roles Endpoints
    # ============================================================
    @app.route("/api/v1/auth/register", methods=["POST"])
    def api_auth_register():
        return auth_controller.register()

    @app.route("/api/v1/auth/login", methods=["POST"])
    def api_auth_login():
        return auth_controller.login()

    @app.route("/api/v1/auth/google", methods=["POST"])
    def api_auth_google():
        return auth_controller.google_auth()

    @app.route("/api/v1/auth/verify", methods=["GET"])
    def api_auth_verify():
        return auth_controller.verify_session()

    @app.route("/api/v1/auth/menu-permissions", methods=["GET"])
    def api_auth_menu_permissions():
        return auth_controller.get_menu_permissions()

    @app.route("/api/v1/auth/roles", methods=["GET"])
    def api_auth_roles():
        return auth_controller.get_registration_roles()

    @app.route("/api/v1/auth/child-login", methods=["POST"])
    def api_auth_child_login():
        return auth_controller.child_login()

    @app.route("/api/v1/auth/refresh", methods=["POST"])
    def api_auth_refresh():
        return auth_controller.refresh()

    @app.route("/api/v1/auth/logout", methods=["POST"])
    def api_auth_logout():
        return auth_controller.logout()

    # ============================================================
    # ============================================================
    # 2.5 Master Data Endpoints
    # ============================================================
    @app.route("/api/v1/master/child-registration-options", methods=["GET"])
    def api_master_child_registration_options():
        return parent_controller.get_child_registration_options()

    # ============================================================
    # 3. Parent Endpoints
    # ============================================================
    @app.route("/api/v1/parent/dashboard", methods=["GET"])
    @app.route("/api/v1/parents/dashboard", methods=["GET"])
    def api_parent_dashboard():
        return parent_controller.get_dashboard()

    @app.route("/api/v1/parents/me", methods=["GET"])
    def api_parent_get_me():
        return parent_controller.get_me()

    @app.route("/api/v1/parents/me/children", methods=["GET"])
    def api_parent_list_children():
        return parent_controller.list_children()

    @app.route("/api/v1/parents/add-child", methods=["POST"])
    @app.route("/api/v1/parents/me/children", methods=["POST"])
    def api_parent_add_child():
        return parent_controller.add_child()

    @app.route("/api/v1/parents/me/children/<student_id>", methods=["PUT"])
    def api_parent_update_child(student_id):
        return parent_controller.update_child(student_id)

    @app.route("/api/v1/parents/me/children/<student_id>", methods=["DELETE"])
    def api_parent_delete_child(student_id):
        return parent_controller.delete_child(student_id)

    @app.route("/api/v1/parents/me/children/<student_id>/overview", methods=["GET"])
    def api_parent_child_overview(student_id):
        return parent_controller.child_overview(student_id)

    @app.route("/api/v1/parents/me/children/<student_id>/learning-path", methods=["GET"])
    def api_parent_child_learning_path(student_id):
        return parent_controller.child_learning_path(student_id)

    # ============================================================
    # 4. Student Endpoints
    # ============================================================
    @app.route("/api/v1/student/dashboard", methods=["GET"])
    @app.route("/api/v1/students/dashboard", methods=["GET"])
    def api_student_dashboard():
        return student_controller.get_dashboard()

    @app.route("/api/v1/students/me", methods=["GET"])
    def api_student_get_me():
        return student_controller.get_me()

    @app.route("/api/v1/students/me/overview", methods=["GET"])
    def api_student_overview():
        return student_controller.my_overview()

    @app.route("/api/v1/students/me/learning-path", methods=["GET"])
    def api_student_learning_path():
        return student_controller.my_learning_path()

    # ============================================================
    # 5. Teacher Endpoints
    # ============================================================
    @app.route("/api/v1/teachers/me/students", methods=["GET"])
    def api_teacher_my_students():
        return teacher_controller.my_students()

    @app.route("/api/v1/teachers/me/students/<student_id>/performance", methods=["GET"])
    def api_teacher_student_performance(student_id):
        return teacher_controller.student_performance(student_id)

    @app.route("/api/v1/teachers/me/students/<student_id>/mastery", methods=["GET"])
    def api_teacher_student_mastery(student_id):
        return teacher_controller.student_mastery(student_id)

    @app.route("/api/v1/teachers/me/students/<student_id>/diagnostics", methods=["GET"])
    def api_teacher_student_diagnostics(student_id):
        return teacher_controller.student_diagnostics(student_id)

    # ============================================================
    # 6. Exam Endpoints
    # ============================================================
    @app.route("/api/v1/exams/generate", methods=["POST"])
    def api_exam_generate():
        return exam_controller.generate_exam()

    @app.route("/api/v1/exams/quick-test", methods=["POST", "GET"])
    def api_exam_quick_test():
        return exam_controller.generate_quick_test()

    @app.route("/api/v1/exams/<exam_id>/submit", methods=["POST"])
    def api_exam_submit(exam_id):
        return exam_controller.submit_exam(exam_id)

    # ============================================================
    # 7. Gamification & Leaderboard Endpoints
    # ============================================================
    @app.route("/api/v1/gamification/badges", methods=["GET"])
    def api_gamification_list_badges():
        return gamification_controller.list_badges()

    @app.route("/api/v1/gamification/award-xp", methods=["POST"])
    def api_gamification_award_xp():
        return gamification_controller.award_xp_route()

    @app.route("/api/v1/leaderboard", methods=["GET"])
    def api_leaderboard():
        return leaderboard_controller.leaderboard()


    # ============================================================
    # 9. Communication & PTC Endpoints
    # ============================================================
    @app.route("/api/v1/teachers", methods=["GET"])
    def api_communication_list_teachers():
        return communication_controller.list_teachers()

    @app.route("/api/v1/conversations", methods=["GET"])
    def api_communication_list_conversations():
        return communication_controller.list_conversations()

    @app.route("/api/v1/conversations/<conversation_id>", methods=["GET"])
    def api_communication_get_conversation(conversation_id):
        return communication_controller.get_conversation(conversation_id)

    @app.route("/api/v1/conversations", methods=["POST"])
    def api_communication_create_conversation():
        return communication_controller.create_or_get_conversation()

    @app.route("/api/v1/conversations/<conversation_id>/messages", methods=["POST"])
    def api_communication_send_message(conversation_id):
        return communication_controller.send_message(conversation_id)

    @app.route("/api/v1/messages/<message_id>/read", methods=["PUT"])
    def api_communication_mark_message_read(message_id):
        return communication_controller.mark_message_read(message_id)

    @app.route("/api/v1/dossiers", methods=["POST"])
    def api_communication_create_dossier():
        return communication_controller.create_dossier()

    @app.route("/api/v1/dossiers", methods=["GET"])
    def api_communication_list_dossiers():
        return communication_controller.list_dossiers()

    @app.route("/api/v1/dossiers/public/<share_token>", methods=["GET"])
    def api_communication_get_public_dossier(share_token):
        return communication_controller.get_public_dossier(share_token)

    @app.route("/api/v1/dossiers/<dossier_id>", methods=["DELETE"])
    def api_communication_delete_dossier(dossier_id):
        return communication_controller.delete_dossier(dossier_id)

    @app.route("/api/v1/dossiers/preview/<student_id>", methods=["GET"])
    def api_communication_preview_student_dossier(student_id):
        return communication_controller.preview_student_dossier(student_id)

    @app.route("/api/v1/ptm/schedule", methods=["POST"])
    def api_communication_schedule_ptm():
        return communication_controller.schedule_ptm()

    @app.route("/api/v1/ptm/schedules", methods=["GET"])
    def api_communication_list_ptm_schedules():
        return communication_controller.list_ptm_schedules()

    # ============================================================
    # 10. Runbook Endpoints
    # ============================================================
    @app.route("/api/v1/runbooks", methods=["GET"])
    def api_runbook_list():
        return runbook_controller.list_runbooks()

    @app.route("/api/v1/runbooks/<runbook_id>", methods=["GET"])
    def api_runbook_get(runbook_id):
        return runbook_controller.get_runbook(runbook_id)

    @app.route("/api/v1/runbooks", methods=["POST"])
    def api_runbook_create():
        return runbook_controller.create_runbook()

    @app.route("/api/v1/runbooks/<runbook_id>", methods=["PUT"])
    def api_runbook_update(runbook_id):
        return runbook_controller.update_runbook(runbook_id)

    @app.route("/api/v1/runbooks/<runbook_id>", methods=["DELETE"])
    def api_runbook_delete(runbook_id):
        return runbook_controller.delete_runbook(runbook_id)

    # ============================================================
    # 11. Admin Endpoints
    # ============================================================
    @app.route("/api/v1/admin/login", methods=["POST"])
    def api_admin_login():
        return auth_controller.admin_login()

    @app.route("/api/v1/admin/reset-password", methods=["POST"])
    def api_admin_reset_password():
        return auth_controller.admin_reset_password()

    @app.route("/api/v1/admin/statistics", methods=["GET"])
    def api_admin_statistics():
        return admin_controller.statistics()

    @app.route("/api/v1/admin/dashboard", methods=["GET"])
    def api_admin_dashboard():
        return admin_controller.admin_dashboard()

    @app.route("/api/v1/admin/users", methods=["GET"])
    def api_admin_list_users():
        return admin_controller.list_users()

    @app.route("/api/v1/admin/students", methods=["GET"])
    def api_admin_list_students():
        return admin_controller.list_students()


    # ============================================================
    # 12. Chat Endpoints
    # ============================================================
    @app.route("/api/v1/chat", methods=["POST"])
    def api_chat():
        return chat_controller.chat()

    # ============================================================
    # 13. Document & File Upload Endpoints
    # ============================================================
    @app.route("/api/v1/files/upload", methods=["POST"])
    def api_files_upload():
        return upload_file_controller.upload_file()

    @app.route("/api/v1/files/<document_id>", methods=["GET"])
    def api_files_get_status(document_id):
        return upload_file_controller.get_document_status(document_id)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.APP_PORT, debug=(config.APP_ENV == "development"))
