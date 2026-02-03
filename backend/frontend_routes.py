"""Frontend serving routes."""
from __future__ import annotations

import os
from functools import lru_cache
from importlib import resources

from flask import Blueprint, jsonify, send_from_directory

from backend import config

frontend_bp = Blueprint("frontend", __name__)


@lru_cache(maxsize=1)
def _resolve_frontend_dist() -> str:
    local_dist = config.FRONTEND_DIST
    if os.path.isdir(local_dist):
        return local_dist
    try:
        dist_path = resources.files("plag_checker_app").joinpath("frontend", "dist")
        if dist_path.is_dir():
            return str(dist_path)
    except (ModuleNotFoundError, AttributeError):
        pass
    return local_dist


@frontend_bp.route("/", defaults={"path": ""})
@frontend_bp.route("/<path:path>")
def serve_frontend(path: str):
    """Serve the built frontend application."""
    frontend_dist = _resolve_frontend_dist()
    if not os.path.isdir(frontend_dist):
        return jsonify({"error": "Frontend build not found"}), 404
    if path and os.path.exists(os.path.join(frontend_dist, path)):
        return send_from_directory(frontend_dist, path)
    return send_from_directory(frontend_dist, "index.html")
