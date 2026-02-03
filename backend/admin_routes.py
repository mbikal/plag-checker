"""Admin endpoints."""
from __future__ import annotations

import os

from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename

from backend import config
from backend.logging_config import get_logger
from backend.request_utils import get_json_body, require_admin, require_username_password
from backend.security import password_error, verify_admin
from backend.users import create_user, load_users, save_users, update_user_password

admin_bp = Blueprint("admin", __name__)
logger = get_logger()


@admin_bp.route("/admin/logs", methods=["POST"])
def admin_logs():
    """Return recent log lines."""
    data = request.json or {}
    limit = int(data.get("limit", 200))
    if not os.path.exists(config.LOG_FILE):
        return jsonify({"lines": []})
    with open(config.LOG_FILE, "r", encoding="utf-8") as log_handle:
        lines = log_handle.readlines()[-limit:]
    return jsonify({"lines": [line.rstrip("\n") for line in lines]})


@admin_bp.route("/admin/teacher", methods=["POST"])
def admin_create_teacher():
    """Create a teacher account (admin only)."""
    data, error = get_json_body()
    if error:
        return error
    admin_username, error = require_admin(data)
    if error:
        return error
    credentials, error = require_username_password(
        data,
        error_message="Username and password are required",
        status_code=400,
    )
    if error:
        return error
    username, password = credentials

    pwd_error = password_error(password)
    if pwd_error:
        return jsonify({"error": pwd_error}), 400

    error_message = create_user(username, password, "teacher")
    if error_message:
        return jsonify({"error": error_message}), 400
    logger.info("Admin created teacher: %s by %s", username, admin_username)
    return jsonify({"message": "Teacher account created"}), 201


@admin_bp.route("/admin/uploads", methods=["POST"])
def admin_uploads():
    """Return list of uploaded scan PDFs (admin only)."""
    data, error = get_json_body()
    if error:
        return error
    admin_username, error = require_admin(data)
    if error:
        return error

    uploads = []
    for name in sorted(os.listdir(config.UPLOAD_DIR)):
        if name.startswith("scan_") and name.endswith(".pdf"):
            uploads.append(
                {
                    "name": name,
                    "url": f"{request.host_url.rstrip('/')}/uploads/{name}",
                }
            )
    return jsonify({"files": uploads})


@admin_bp.route("/admin/users", methods=["POST"])
def admin_users():
    """List users for admin control."""
    data, error = get_json_body()
    if error:
        return error
    _, error = require_admin(data)
    if error:
        return error

    users = load_users()
    payload = [
        {"username": name, "role": info.get("role", "student")}
        for name, info in users.items()
    ]
    return jsonify({"users": payload})


@admin_bp.route("/admin/users/role", methods=["POST"])
def admin_update_role():
    """Update a user's role (admin only)."""
    data, error = get_json_body()
    if error:
        return error
    admin_username, error = require_admin(data)
    if error:
        return error
    username = data.get("username")
    role = data.get("role")
    if not username or not role:
        return jsonify({"error": "Username and role are required"}), 400
    if role not in {"student", "teacher", "admin"}:
        return jsonify({"error": "Invalid role"}), 400

    users = load_users()
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    users[username]["role"] = role
    save_users(users)
    logger.info("Admin updated role: %s -> %s by %s", username, role, admin_username)
    return jsonify({"message": "Role updated"})


@admin_bp.route("/admin/users/delete", methods=["POST"])
def admin_delete_user():
    """Delete a user account (admin only)."""
    data, error = get_json_body()
    if error:
        return error
    admin_username, error = require_admin(data)
    if error:
        return error
    username = data.get("username")
    if not username:
        return jsonify({"error": "Username required"}), 400
    if username == admin_username:
        return jsonify({"error": "Cannot delete your own account"}), 400

    users = load_users()
    if username not in users:
        return jsonify({"error": "User not found"}), 404
    users.pop(username)
    save_users(users)
    logger.info("Admin deleted user: %s by %s", username, admin_username)
    return jsonify({"message": "User deleted"})


@admin_bp.route("/admin/users/reset", methods=["POST"])
def admin_reset_password():
    """Reset a user's password (admin only)."""
    data, error = get_json_body()
    if error:
        return error
    admin_username, error = require_admin(data)
    if error:
        return error
    credentials, error = require_username_password(
        data,
        error_message="Username and password are required",
        status_code=400,
    )
    if error:
        return error
    username, password = credentials

    pwd_error = password_error(password)
    if pwd_error:
        return jsonify({"error": pwd_error}), 400

    error_message = update_user_password(username, password)
    if error_message:
        return jsonify({"error": error_message}), 404
    logger.info("Admin reset password: %s by %s", username, admin_username)
    return jsonify({"message": "Password reset"})


@admin_bp.route("/admin/corpus/list", methods=["POST"])
def admin_corpus_list():
    """List corpus files (admin only)."""
    data, error = get_json_body()
    if error:
        return error
    _, error = require_admin(data)
    if error:
        return error

    files = sorted(
        name for name in os.listdir(config.CORPUS_DIR)
        if name.lower().endswith(".pdf")
    )
    return jsonify({"files": files})


@admin_bp.route("/admin/corpus/upload", methods=["POST"])
def admin_corpus_upload():
    """Upload a PDF into the corpus (admin only)."""
    admin_username = request.form.get("admin_username")
    admin_password = request.form.get("admin_password")
    if not admin_username or not admin_password:
        return jsonify({"error": "Admin credentials required"}), 401
    if not verify_admin(admin_username, admin_password):
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "File is required"}), 400
    uploaded = request.files["file"]
    if not uploaded.filename:
        return jsonify({"error": "Filename is required"}), 400
    if not uploaded.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400
    if uploaded.mimetype not in ("application/pdf", "application/x-pdf"):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(uploaded.filename)
    dest_path = os.path.join(config.CORPUS_DIR, filename)
    uploaded.save(dest_path)
    logger.info("Admin uploaded corpus file: %s by %s", filename, admin_username)
    return jsonify({"message": "Corpus file uploaded"}), 201


@admin_bp.route("/admin/corpus/delete", methods=["POST"])
def admin_corpus_delete():
    """Delete a corpus PDF (admin only)."""
    data, error = get_json_body()
    if error:
        return error
    admin_username, error = require_admin(data)
    if error:
        return error
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "Filename required"}), 400
    if not filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    file_path = os.path.join(config.CORPUS_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    os.remove(file_path)
    logger.info("Admin deleted corpus file: %s by %s", filename, admin_username)
    return jsonify({"message": "Corpus file deleted"})


@admin_bp.route("/admin/corpus/file/<filename>", methods=["GET"])
def admin_corpus_file(filename: str):
    """Serve a corpus PDF (admin only)."""
    admin_username = request.args.get("admin_username")
    admin_password = request.args.get("admin_password")
    if not admin_username or not admin_password:
        return jsonify({"error": "Admin credentials required"}), 401
    if not verify_admin(admin_username, admin_password):
        return jsonify({"error": "Unauthorized"}), 401
    if not filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400
    file_path = os.path.join(config.CORPUS_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path, mimetype="application/pdf")
