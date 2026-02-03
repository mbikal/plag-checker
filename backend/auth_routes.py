"""Authentication endpoints."""
from __future__ import annotations

import bcrypt
from flask import Blueprint, jsonify

from backend.ca import generate_certificate
from backend.logging_config import get_logger
from backend.request_utils import get_json_body, require_username_password_or_error
from backend.security import password_error
from backend.users import create_user, load_users

auth_bp = Blueprint("auth", __name__)
logger = get_logger()


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Handle user registration."""
    data, error = get_json_body()
    if error:
        return error

    credentials = require_username_password_or_error(
        data,
        error_message="Username and password are required",
        status_code=400,
    )
    if isinstance(credentials, tuple) and len(credentials) == 2:
        username, password = credentials
    else:
        return credentials
    role = data.get("role", "student")

    pwd_error = password_error(password)
    if pwd_error:
        return jsonify({"error": pwd_error}), 400

    error_message = create_user(username, password, role)
    if error_message:
        logger.info("Signup failed: username exists (%s)", username)
        return jsonify({"error": error_message}), 400

    logger.info("Signup success: %s (%s)", username, role)
    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Handle user login and certificate generation."""
    data, error = get_json_body()
    if error:
        return error

    credentials = require_username_password_or_error(
        data,
        error_message="Invalid username or password",
        status_code=401,
    )
    if isinstance(credentials, tuple) and len(credentials) == 2:
        username, password = credentials
    else:
        logger.info("Login failed: missing credentials")
        return credentials

    users = load_users()
    if username not in users:
        logger.info("Login failed: user not found (%s)", username)
        return jsonify({"error": "Invalid username or password"}), 401

    stored_password = users[username]["password"].encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), stored_password):
        logger.info("Login failed: bad password (%s)", username)
        return jsonify({"error": "Invalid username or password"}), 401

    role = users[username]["role"]
    cert_path = generate_certificate(username, role)

    logger.info("Login success: %s (%s)", username, role)
    return jsonify(
        {
            "message": "Login successful",
            "role": role,
            "certificate_path": cert_path,
        }
    )
