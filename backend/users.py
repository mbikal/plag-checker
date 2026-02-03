"""User storage helpers."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

import bcrypt

from backend import config


def load_users() -> Dict[str, Any]:
    """Load users from JSON file."""
    if os.path.exists(config.USERS_FILE):
        with open(config.USERS_FILE, "r", encoding="utf-8") as file_handle:
            try:
                return json.load(file_handle)
            except json.JSONDecodeError:
                return {}
    return {}


def save_users(users: Dict[str, Any]) -> None:
    """Persist users to JSON file."""
    with open(config.USERS_FILE, "w", encoding="utf-8") as file_handle:
        json.dump(users, file_handle, indent=4)


def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_user(username: str, password: str, role: str) -> str | None:
    """Create a new user and return an error message if it fails."""
    users = load_users()
    if username in users:
        return "Username already exists"
    users[username] = {"password": hash_password(password), "role": role}
    save_users(users)
    return None


def update_user_password(username: str, password: str) -> str | None:
    """Update a user's password and return an error message if it fails."""
    users = load_users()
    if username not in users:
        return "User not found"
    users[username]["password"] = hash_password(password)
    save_users(users)
    return None
