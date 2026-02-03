"""Security utilities for auth and admin actions."""
from __future__ import annotations

import re

import bcrypt

from backend.users import load_users


def password_error(password: str) -> str | None:
    """Return a validation error message for invalid passwords."""
    if not isinstance(password, str):
        return "Password must be a string"
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    checks = [
        (r"[A-Z]", "Password must include an uppercase letter"),
        (r"[a-z]", "Password must include a lowercase letter"),
        (r"\d", "Password must include a number"),
        (r"[^A-Za-z0-9]", "Password must include a symbol"),
    ]
    for pattern, message in checks:
        if not re.search(pattern, password):
            return message
    return None


def verify_admin(admin_username: str, admin_password: str) -> bool:
    """Check admin credentials."""
    users = load_users()
    if admin_username not in users:
        return False
    if users[admin_username].get("role") != "admin":
        return False
    stored_password = users[admin_username]["password"].encode("utf-8")
    return bcrypt.checkpw(admin_password.encode("utf-8"), stored_password)


def verify_teacher(username: str, password: str) -> bool:
    """Check teacher credentials (or admin)."""
    users = load_users()
    if username not in users:
        return False
    role = users[username].get("role")
    if role not in {"teacher", "admin"}:
        return False
    stored_password = users[username]["password"].encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), stored_password)
