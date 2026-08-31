"""AcuGrade AI backend entry point.

app.py stays deliberately thin per the master prompt's §3: it wires up
Flask, CORS, middleware, and controller blueprints, and contains no business
logic of its own. Run with:

    python app.py                 # dev server
    gunicorn -w 4 -b 0.0.0.0:8000 app:app   # production (see README.md)
"""
import time

from flask import Flask, g, request
from flask_cors import CORS

from controller import register_all
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
    register_all(app)

    @app.before_request
    def _before():
        g._start_time = time.time()
        if request.path != "/api/v1/health":
            rate_limit()

    @app.after_request
    def _after(response):
        duration_ms = (time.time() - getattr(g, "_start_time", time.time())) * 1000
        log_request(request.method, request.path, response.status_code, duration_ms,
                    getattr(g, "current_user_id", None))
        # Secure headers (master prompt §34)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.APP_PORT, debug=(config.APP_ENV == "development"))
