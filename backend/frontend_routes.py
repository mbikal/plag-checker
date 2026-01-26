"""Frontend serving routes."""
from __future__ import annotations

import importlib.resources as resources
import os

from flask import Blueprint, jsonify, send_from_directory

from backend import config

frontend_bp = Blueprint("frontend", __name__)
_frontend_dist = None


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
    global _frontend_dist
    if _frontend_dist is None:
        _frontend_dist = _resolve_frontend_dist()
    if not os.path.isdir(_frontend_dist):
        return jsonify({"error": "Frontend build not found"}), 404
    if path and os.path.exists(os.path.join(_frontend_dist, path)):
        return send_from_directory(_frontend_dist, path)
    return send_from_directory(_frontend_dist, "index.html")
