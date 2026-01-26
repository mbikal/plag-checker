"""
Tests for plagiarism checker module.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checker import analyze_and_sign, analyze_file, ensure_keypair  # pylint: disable=import-error


def _write_pdf(path: Path, content: str) -> None:
    """Write a simple single-page PDF for tests."""
    canvas_obj = canvas.Canvas(str(path))
    canvas_obj.drawString(72, 720, content)
    canvas_obj.save()


def test_analyze_file_basic(tmp_path: Path) -> None:
    """Ensure analyze_file returns expected report data."""
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    sample_corpus = corpus_dir / "corpus.pdf"
    _write_pdf(sample_corpus, "This is a sample document used for comparison.")

    target_file = tmp_path / "target.pdf"
    _write_pdf(target_file, "This is a sample document used for comparison and testing.")

    report = analyze_file(target_file, corpus_dir=corpus_dir)

    assert report["file"].endswith("target.pdf")
    assert report["sha256"]
    assert report["word_count"] > 0
    assert report["unique_words"] > 0
    assert report["matches"]
    assert report["matches"][0]["score"] > 0


def test_analyze_and_sign(tmp_path: Path) -> None:
    """Ensure analyze_and_sign returns signed report data."""
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    sample_corpus = corpus_dir / "corpus.pdf"
    _write_pdf(sample_corpus, "A second sample document to check similarity.")

    target_file = tmp_path / "target.pdf"
    _write_pdf(target_file, "A second sample document to check similarity and signatures.")

    key_dir = tmp_path / "keys"
    report = analyze_and_sign(target_file, corpus_dir=corpus_dir, key_dir=key_dir)

    assert "signature" in report
    assert "public_key" in report
    assert Path(key_dir / "signing_private.pem").exists()
    assert Path(key_dir / "signing_public.pem").exists()
    assert json.loads(json.dumps(report))


def test_ensure_keypair_idempotent(tmp_path: Path) -> None:
    """Ensure keypair creation is idempotent."""
    key_dir = tmp_path / "keys"
    private_path, public_path = ensure_keypair(key_dir=key_dir)
    private_path_2, public_path_2 = ensure_keypair(key_dir=key_dir)

    assert private_path == private_path_2
    assert public_path == public_path_2
    assert private_path.exists()
    assert public_path.exists()


if __name__ == "__main__":
    test_analyze_file_basic(Path("._tmp"))
    test_analyze_and_sign(Path("._tmp"))
    test_ensure_keypair_idempotent(Path("._tmp"))
    print("plag-system/test.py: ok")
