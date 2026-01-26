"""Authentication endpoints."""
from __future__ import annotations

import bcrypt
from flask import Blueprint, jsonify, request

from backend.ca import generate_certificate
from backend.logging_config import get_logger
from backend.security import password_error
from backend.users import load_users, save_users

auth_bp = Blueprint("auth", __name__)
logger = get_logger()


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Handle user registration."""
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400

    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "student")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    pwd_error = password_error(password)
    if pwd_error:
        return jsonify({"error": pwd_error}), 400

    users = load_users()
    if username in users:
        logger.info("Signup failed: username exists (%s)", username)
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    users[username] = {"password": hashed_password, "role": role}
    save_users(users)

    logger.info("Signup success: %s (%s)", username, role)
    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Handle user login and certificate generation."""
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400

    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        logger.info("Login failed: missing credentials")
        return jsonify({"error": "Invalid username or password"}), 401

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
