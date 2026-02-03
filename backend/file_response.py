"""Helpers for sending decrypted files."""
from __future__ import annotations

import os

from flask import after_this_request, send_file

from backend.crypto_storage import decrypt_to_temp


def send_decrypted_pdf(file_path: str) -> "Response":
    """Send a decrypted PDF and clean up the temporary file."""
    temp_path = decrypt_to_temp(file_path)

    @after_this_request
    def _cleanup(response):
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return response

    return send_file(temp_path, mimetype="application/pdf")
