"""Registers every controller blueprint. app.py calls register_all(app) once."""


def register_all(app):
    from controller.auth_controller import auth_bp
    from controller.parent_controller import parent_bp
    from controller.student_controller import student_bp
    from controller.teacher_controller import teacher_bp
    from controller.exam_controller import exam_bp
    from controller.runbook_controller import runbook_bp
    from controller.gamification_controller import gamification_bp
    from controller.leaderboard_controller import leaderboard_bp
    from controller.communication_controller import communication_bp
    from controller.subscription_controller import subscription_bp
    from controller.admin_controller import admin_bp
    from controller.health_controller import health_bp
    from controller.upload_file_controller import upload_bp

    for blueprint in (
        auth_bp, parent_bp, student_bp, teacher_bp, exam_bp, runbook_bp,
        gamification_bp, leaderboard_bp, communication_bp, subscription_bp,
        admin_bp, health_bp, upload_bp,
    ):
        app.register_blueprint(blueprint)
