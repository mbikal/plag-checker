"""Flask application factory."""
from __future__ import annotations

from flask import Flask

from backend.admin_routes import admin_bp
from backend.auth_routes import auth_bp
from backend.frontend_routes import frontend_bp
from backend.scan_routes import scan_bp
from backend.teacher_routes import teacher_bp


def create_app() -> Flask:
    """Create and configure the Flask app."""
    app = Flask(__name__)

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    app.register_blueprint(auth_bp)
    app.register_blueprint(scan_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(frontend_bp)

    return app
