"""Configuration for backend paths."""
from __future__ import annotations

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
CA_DIR = os.path.join(BASE_DIR, "ca")
CERT_DIR = os.path.join(BASE_DIR, "certs")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
LOG_FILE = os.path.join(BASE_DIR, "app.log")
CORPUS_DIR = os.path.join(BASE_DIR, "plag_system", "corpus")
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
MASTER_KEY_FILE = os.path.join(BASE_DIR, "keys", "master.key")

os.makedirs(CA_DIR, exist_ok=True)
os.makedirs(CERT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CORPUS_DIR, exist_ok=True)
