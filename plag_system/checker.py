"""
Plagiarism checker with report signing.
Designed for backend module use.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives.asymmetric import ed25519
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.pdfgen import canvas


DEFAULT_CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
DEFAULT_KEYS_DIR = Path(__file__).resolve().parent / "keys"
DEFAULT_KEYSTORE_NAME = "signing_key.p12"
_LOGGER = logging.getLogger(__name__)


def _read_text(path: Path) -> str:
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")
    with pdfplumber.open(str(path)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def _normalize(text: str) -> str:
    return " ".join("".join(ch.lower() if ch.isalnum() else " " for ch in text).split())


def _ngrams(text: str, n: int = 3) -> set[str]:
    tokens = _normalize(text).split()
    if len(tokens) < n:
        return set()
    return {" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence for sentence in parts if sentence]


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def _get_keystore_password() -> bytes:
    password = os.getenv("PLAG_KEYSTORE_PASSWORD")
    if not password:
        _LOGGER.warning(
            "PLAG_KEYSTORE_PASSWORD not set. Using development-only default password."
        )
        password = "plag-checker-dev"
    return password.encode("utf-8")


def ensure_keypair(key_dir: Path | str = DEFAULT_KEYS_DIR) -> tuple[Path, bytes]:
    """
    Ensure a PKCS#12 keystore exists and return (keystore_path, public_key_pem).
    """
    key_dir = Path(key_dir)
    key_dir.mkdir(parents=True, exist_ok=True)
    keystore_path = key_dir / DEFAULT_KEYSTORE_NAME
    password = _get_keystore_password()

    if keystore_path.exists():
        key, _, _ = pkcs12.load_key_and_certificates(keystore_path.read_bytes(), password)
        if key is None:
            raise ValueError("Keystore is missing a private key.")
        public_key = key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return keystore_path, public_bytes

    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    keystore_bytes = pkcs12.serialize_key_and_certificates(
        name=b"plag-checker-signing",
        key=private_key,
        cert=None,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password),
    )
    keystore_path.write_bytes(keystore_bytes)
    return keystore_path, public_bytes


@dataclass
class MatchResult:
    """Container for a similarity match."""
    path: str
    score: float


def _iter_corpus_files(corpus_dir: Path) -> Iterable[Path]:
    if not corpus_dir.exists():
        return []
    return [p for p in corpus_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]


def analyze_file(  # pylint: disable=too-many-locals
    file_path: Path | str,
    corpus_dir: Path | str = DEFAULT_CORPUS_DIR,
) -> dict:
    """
    Analyze a single file against a local corpus and return a JSON-ready report.
    """
    path = Path(file_path)
    text = _read_text(path)
    file_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    grams = _ngrams(text)

    corpus_dir = Path(corpus_dir)
    matches: list[MatchResult] = []
    unique_matches: set[str] = set()
    for corpus_file in _iter_corpus_files(corpus_dir):
        corpus_text = _read_text(corpus_file)
        corpus_grams = _ngrams(corpus_text)
        overlap = grams & corpus_grams
        unique_matches |= overlap
        score = _jaccard(grams, corpus_grams)
        if score > 0:
            matches.append(MatchResult(path=str(corpus_file), score=round(score, 4)))

    matches.sort(key=lambda item: item.score, reverse=True)
    top_score = matches[0].score if matches else 0.0

    sentences = _sentences(text)
    matching_sentences = 0
    for sentence in sentences:
        sentence_grams = _ngrams(sentence)
        if sentence_grams and (sentence_grams & unique_matches):
            matching_sentences += 1

    total_sentences = len(sentences)
    non_matching_sentences = max(total_sentences - matching_sentences, 0)

    return {
        "file": str(path),
        "sha256": file_hash,
        "word_count": len(_normalize(text).split()),
        "unique_words": len(set(_normalize(text).split())),
        "matches": [match.__dict__ for match in matches[:10]],
        "similarity_percent": round(top_score * 100, 2),
        "matching_ngrams": len(unique_matches),
        "plagiarism_percentage": (
            round((len(unique_matches) / len(grams)) * 100, 2) if grams else 0.0
        ),
        "total_sentences": total_sentences,
        "matching_sentences": matching_sentences,
        "non_matching_sentences": non_matching_sentences,
    }


def analyze_and_sign(
    file_path: Path | str,
    corpus_dir: Path | str = DEFAULT_CORPUS_DIR,
    key_dir: Path | str = DEFAULT_KEYS_DIR,
    annotated_pdf_path: Path | str | None = None,
) -> dict:
    """
    Analyze the file and sign the report for integrity verification.
    """
    report = analyze_file(file_path, corpus_dir=corpus_dir)
    if annotated_pdf_path:
        annotate_pdf(file_path, corpus_dir=corpus_dir, output_path=annotated_pdf_path)
    keystore_path, public_key_pem = ensure_keypair(key_dir=key_dir)
    password = _get_keystore_password()
    private_key, _, _ = pkcs12.load_key_and_certificates(
        keystore_path.read_bytes(),
        password,
    )
    if private_key is None:
        raise ValueError("Signing keystore did not contain a private key.")
    payload = json.dumps(report, sort_keys=True).encode("utf-8")
    signature = private_key.sign(payload)

    report["signature"] = signature.hex()
    report["public_key"] = public_key_pem.decode("utf-8")
    return report


def annotate_pdf(  # pylint: disable=too-many-locals
    file_path: Path | str,
    corpus_dir: Path | str = DEFAULT_CORPUS_DIR,
    output_path: Path | str = "annotated.pdf",
    ngram_size: int = 3,
) -> Path:
    """
    Generate an annotated PDF highlighting matched n-grams.
    """
    file_path = Path(file_path)
    corpus_dir = Path(corpus_dir)
    output_path = Path(output_path)

    corpus_ngrams: set[str] = set()
    for corpus_file in _iter_corpus_files(corpus_dir):
        corpus_text = _read_text(corpus_file)
        corpus_ngrams |= _ngrams(corpus_text, n=ngram_size)

    reader = PdfReader(str(file_path))
    writer = PdfWriter()

    with pdfplumber.open(str(file_path)) as pdf:
        for page_index, page in enumerate(pdf.pages):
            words = page.extract_words() or []
            tokens = []
            for word in words:
                token = _normalize(word.get("text", ""))
                tokens.append(token)

            marked_indices: set[int] = set()
            for idx in range(len(tokens) - ngram_size + 1):
                ngram = " ".join(tokens[idx : idx + ngram_size])
                if ngram and ngram in corpus_ngrams:
                    marked_indices.update(range(idx, idx + ngram_size))

            overlay_path = output_path.with_suffix(f".overlay.{page_index}.pdf")
            page_width = float(page.width)
            page_height = float(page.height)
            overlay_canvas = canvas.Canvas(str(overlay_path), pagesize=(page_width, page_height))
            overlay_canvas.setFillColor(colors.Color(1, 0.95, 0.4, alpha=0.35))
            overlay_canvas.setStrokeColor(colors.Color(1, 0.85, 0.2, alpha=0.0))

            for idx in marked_indices:
                if idx >= len(words):
                    continue
                word = words[idx]
                x0 = float(word["x0"])
                x1 = float(word["x1"])
                top = float(word["top"])
                bottom = float(word["bottom"])
                y0 = page_height - bottom
                height = bottom - top
                overlay_canvas.rect(x0, y0, x1 - x0, height, fill=1, stroke=0)

            overlay_canvas.save()

            base_page = reader.pages[page_index]
            overlay_reader = PdfReader(str(overlay_path))
            base_page.merge_page(overlay_reader.pages[0])
            writer.add_page(base_page)
            if overlay_path.exists():
                overlay_path.unlink()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as output_handle:
        writer.write(output_handle)

    return output_path
