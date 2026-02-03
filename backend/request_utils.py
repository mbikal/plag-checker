"""Request helpers for validating JSON and credentials."""
from __future__ import annotations

from typing import Any

from flask import jsonify, request

from backend.security import verify_admin, verify_teacher


def get_json_body() -> tuple[dict[str, Any] | None, tuple[Any, int] | None]:
    """Return JSON body or an error response tuple."""
    if not request.is_json:
        return None, (jsonify({"error": "JSON body required"}), 400)
    return request.json or {}, None


def require_admin(
    data: dict[str, Any],
) -> tuple[str | None, tuple[Any, int] | None]:
    """Validate admin credentials from JSON body."""
    admin_username = data.get("admin_username")
    admin_password = data.get("admin_password")
    if not admin_username or not admin_password:
        return None, (jsonify({"error": "Admin credentials required"}), 401)
    if not verify_admin(admin_username, admin_password):
        return None, (jsonify({"error": "Unauthorized"}), 401)
    return admin_username, None


def require_teacher(
    data: dict[str, Any],
) -> tuple[tuple[str, str] | None, tuple[Any, int] | None]:
    """Validate teacher credentials from JSON body."""
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return None, (jsonify({"error": "Credentials required"}), 401)
    if not verify_teacher(username, password):
        return None, (jsonify({"error": "Unauthorized"}), 401)
    return (username, password), None


def require_username_password(
    data: dict[str, Any],
    error_message: str,
    status_code: int,
) -> tuple[tuple[str, str] | None, tuple[Any, int] | None]:
    """Validate username/password from JSON body with custom error."""
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return None, (jsonify({"error": error_message}), status_code)
    return (username, password), None


def require_username_password_or_error(
    data: dict[str, Any],
    error_message: str,
    status_code: int,
) -> tuple[str, str] | tuple[Any, int]:
    """Return credentials or a Flask error response tuple."""
    credentials, error = require_username_password(data, error_message, status_code)
    if error:
        return error
    return credentials


def require_admin_form() -> tuple[str | None, tuple[Any, int] | None]:
    """Validate admin credentials from multipart form data."""
    admin_username = request.form.get("admin_username")
    admin_password = request.form.get("admin_password")
    if not admin_username or not admin_password:
        return None, (jsonify({"error": "Admin credentials required"}), 401)
    if not verify_admin(admin_username, admin_password):
        return None, (jsonify({"error": "Unauthorized"}), 401)
    return admin_username, None


def require_admin_query() -> tuple[str | None, tuple[Any, int] | None]:
    """Validate admin credentials from query parameters."""
    admin_username = request.args.get("admin_username")
    admin_password = request.args.get("admin_password")
    if not admin_username or not admin_password:
        return None, (jsonify({"error": "Admin credentials required"}), 401)
    if not verify_admin(admin_username, admin_password):
        return None, (jsonify({"error": "Unauthorized"}), 401)
    return admin_username, None
