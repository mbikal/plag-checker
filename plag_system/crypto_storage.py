"""Hybrid encryption helpers for corpus storage."""
# pylint: disable=duplicate-code
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"PLAGENC1"
NONCE_SIZE = 12
DATA_KEY_SIZE = 32
WRAPPED_KEY_SIZE = DATA_KEY_SIZE + 16


def _master_key_path() -> Path:
    base_dir = Path(__file__).resolve().parents[1]
    return base_dir / "keys" / "master.key"


def _ensure_master_key() -> bytes:
    key_path = _master_key_path()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        return key_path.read_bytes()
    key = os.urandom(DATA_KEY_SIZE)
    fd = os.open(str(key_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(key)
    return key


def decrypt_if_needed(payload: bytes) -> bytes:
    """Decrypt payload if it has the encryption header."""
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


def is_encrypted(payload: bytes) -> bool:
    """Check if payload has the encryption header."""
    return payload.startswith(MAGIC)


def decrypt_to_temp(path: Path, suffix: str = ".pdf") -> Path:
    """Decrypt a file into a temporary path and return it."""
    payload = path.read_bytes()
    plaintext = decrypt_if_needed(payload)
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(plaintext)
        return Path(temp_file.name)
