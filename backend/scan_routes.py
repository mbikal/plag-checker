"""Plagiarism scan endpoints."""
from __future__ import annotations

import json
import os
import tempfile

from flask import Blueprint, jsonify, request, send_file, after_this_request
from werkzeug.utils import secure_filename

from backend import config
from backend.crypto_storage import decrypt_to_temp, encrypt_file_in_place
from backend.logging_config import get_logger
from plag_system.checker import analyze_and_sign

scan_bp = Blueprint("scan", __name__)
logger = get_logger()


@scan_bp.route("/scan", methods=["POST"])
def scan():
    """Handle file upload and plagiarism scan."""
    if "file" not in request.files:
        logger.info("Scan failed: file missing")
        return jsonify({"error": "File is required"}), 400

    uploaded = request.files["file"]
    if not uploaded.filename:
        logger.info("Scan failed: filename missing")
        return jsonify({"error": "Filename is required"}), 400
    if not uploaded.filename.lower().endswith(".pdf"):
        logger.info("Scan failed: non-pdf filename")
        return jsonify({"error": "Only PDF files are supported"}), 400
    if uploaded.mimetype not in ("application/pdf", "application/x-pdf"):
        logger.info("Scan failed: invalid mimetype (%s)", uploaded.mimetype)
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(uploaded.filename)
    with tempfile.NamedTemporaryFile(
        dir=config.UPLOAD_DIR,
        suffix=f"_{filename}",
        delete=False,
    ) as temp_file:
        uploaded.save(temp_file.name)
        temp_path = temp_file.name

    scan_id = os.urandom(8).hex()
    annotated_path = os.path.join(config.UPLOAD_DIR, f"scan_{scan_id}.pdf")
    summary_path = os.path.join(config.UPLOAD_DIR, f"scan_{scan_id}.json")
    try:
        report = analyze_and_sign(temp_path, annotated_pdf_path=annotated_path)
        encrypt_file_in_place(annotated_path)
    except ValueError as exc:
        logger.info("Scan failed: %s", exc)
        return jsonify({"error": str(exc)}), 400
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    response = dict(report)
    base_url = request.host_url.rstrip("/")
    response["pdf_url"] = f"{base_url}/scan/{scan_id}/pdf"
    logger.info("Scan success: %s", filename)
    summary = {
        "scan_id": scan_id,
        "file": filename,
        "matching_sentences": report.get("matching_sentences"),
        "total_sentences": report.get("total_sentences"),
        "plagiarism_percentage": report.get("plagiarism_percentage"),
    }
    try:
        with open(summary_path, "w", encoding="utf-8") as summary_handle:
            json.dump(summary, summary_handle)
    except OSError:
        logger.info("Scan summary write failed: %s", summary_path)
    return jsonify(response)


@scan_bp.route("/scan/<scan_id>/pdf", methods=["GET"])
def scan_pdf(scan_id: str):
    """Serve annotated PDF for a completed scan."""
    filename = f"scan_{scan_id}.pdf"
    pdf_path = os.path.join(config.UPLOAD_DIR, filename)
    if not os.path.exists(pdf_path):
        logger.info("Scan PDF not found: %s", scan_id)
        return jsonify({"error": "Scan not found"}), 404
    temp_path = decrypt_to_temp(pdf_path)

    @after_this_request
    def _cleanup(response):
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return response

    return send_file(temp_path, mimetype="application/pdf")


@scan_bp.route("/uploads/<filename>", methods=["GET"])
def upload_file(filename: str):
    """Serve uploaded scan PDF files."""
    if not filename.startswith("scan_") or not filename.endswith(".pdf"):
        return jsonify({"error": "Not found"}), 404
    file_path = os.path.join(config.UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Not found"}), 404
    temp_path = decrypt_to_temp(file_path)

    @after_this_request
    def _cleanup(response):
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return response

    return send_file(temp_path, mimetype="application/pdf")
