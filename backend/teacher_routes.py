"""Teacher endpoints."""
from __future__ import annotations

import json
import os

from flask import Blueprint, jsonify, request

from backend import config
from backend.request_utils import get_json_body, require_teacher

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

    uploads = []
    for name in sorted(os.listdir(config.UPLOAD_DIR)):
        if name.startswith("scan_") and name.endswith(".pdf"):
            summary_path = os.path.join(
                config.UPLOAD_DIR,
                name.replace(".pdf", ".json"),
            )
            summary = {}
            if os.path.exists(summary_path):
                try:
                    with open(summary_path, "r", encoding="utf-8") as summary_handle:
                        summary = json.load(summary_handle)
                except (OSError, json.JSONDecodeError):
                    summary = {}
            uploads.append(
                {
                    "name": name,
                    "url": f"{request.host_url.rstrip('/')}/uploads/{name}",
                    "matching_sentences": summary.get("matching_sentences"),
                    "total_sentences": summary.get("total_sentences"),
                    "plagiarism_percentage": summary.get("plagiarism_percentage"),
                }
            )
    return jsonify({"files": uploads})
