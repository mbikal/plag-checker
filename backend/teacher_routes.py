"""Teacher endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.request_utils import get_json_body, require_teacher
from backend.uploads import list_scan_uploads

teacher_bp = Blueprint("teacher", __name__)


@teacher_bp.route("/teacher/uploads", methods=["POST"])
def teacher_uploads():
    """Return list of uploaded scan PDFs for teachers."""
    data, error = get_json_body()
    if error:
        return error
    _, error = require_teacher(data)
    if error:
        return error

    return jsonify({"files": list_scan_uploads(request, include_summary=True)})
