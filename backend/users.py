"""User storage helpers."""
from __future__ import annotations

import json
import os
from typing import Dict, Any

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
