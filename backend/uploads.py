"""Helpers for scan uploads."""
from __future__ import annotations

import json
import os
from typing import Any

from flask import Request

from backend import config


def list_scan_uploads(request: Request, include_summary: bool = False) -> list[dict[str, Any]]:
    """Return scan PDF metadata for the uploads directory."""
    uploads: list[dict[str, Any]] = []
    for name in sorted(os.listdir(config.UPLOAD_DIR)):
        if not (name.startswith("scan_") and name.endswith(".pdf")):
            continue
        item: dict[str, Any] = {
            "name": name,
            "url": f"{request.host_url.rstrip('/')}/uploads/{name}",
        }
        if include_summary:
            summary_path = os.path.join(config.UPLOAD_DIR, name.replace(".pdf", ".json"))
            summary = {}
            if os.path.exists(summary_path):
                try:
                    with open(summary_path, "r", encoding="utf-8") as summary_handle:
                        summary = json.load(summary_handle)
                except (OSError, json.JSONDecodeError):
                    summary = {}
            item.update(
                {
                    "matching_sentences": summary.get("matching_sentences"),
                    "total_sentences": summary.get("total_sentences"),
                    "plagiarism_percentage": summary.get("plagiarism_percentage"),
                }
            )
        uploads.append(item)
    return uploads
