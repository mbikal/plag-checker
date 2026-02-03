"""Hybrid encryption helpers for file storage."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from backend import config

MAGIC = b"PLAGENC1"
NONCE_SIZE = 12
DATA_KEY_SIZE = 32
WRAPPED_KEY_SIZE = DATA_KEY_SIZE + 16


def _ensure_master_key() -> bytes:
    key_path = Path(config.MASTER_KEY_FILE)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        return key_path.read_bytes()
    key = os.urandom(DATA_KEY_SIZE)
    fd = os.open(str(key_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(key)
    return key


def _encrypt_bytes(plaintext: bytes) -> bytes:
    master_key = _ensure_master_key()
    data_key = os.urandom(DATA_KEY_SIZE)
    wrap_nonce = os.urandom(NONCE_SIZE)
    data_nonce = os.urandom(NONCE_SIZE)
    wrapped_key = AESGCM(master_key).encrypt(wrap_nonce, data_key, None)
    ciphertext = AESGCM(data_key).encrypt(data_nonce, plaintext, None)
    return MAGIC + wrap_nonce + data_nonce + wrapped_key + ciphertext


def _decrypt_bytes(payload: bytes) -> bytes:
    if not payload.startswith(MAGIC):
        return payload
    offset = len(MAGIC)
    wrap_nonce = payload[offset : offset + NONCE_SIZE]
    offset += NONCE_SIZE
    data_nonce = payload[offset : offset + NONCE_SIZE]
    offset += NONCE_SIZE
    wrapped_key = payload[offset : offset + WRAPPED_KEY_SIZE]
    offset += WRAPPED_KEY_SIZE
    ciphertext = payload[offset:]
    master_key = _ensure_master_key()
    data_key = AESGCM(master_key).decrypt(wrap_nonce, wrapped_key, None)
    return AESGCM(data_key).decrypt(data_nonce, ciphertext, None)


def encrypt_file_in_place(path: str | Path) -> None:
    file_path = Path(path)
    payload = file_path.read_bytes()
    if payload.startswith(MAGIC):
        return
    file_path.write_bytes(_encrypt_bytes(payload))


def decrypt_to_temp(path: str | Path, suffix: str = ".pdf") -> Path:
    file_path = Path(path)
    payload = file_path.read_bytes()
    plaintext = _decrypt_bytes(payload)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(plaintext)
    temp_file.flush()
    temp_file.close()
    return Path(temp_file.name)
