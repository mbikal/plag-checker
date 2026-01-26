"""Plagiarism system helpers."""
# pylint: disable=invalid-name

try:
    from .checker import analyze_and_sign, analyze_file, annotate_pdf, ensure_keypair
except ImportError:  # pragma: no cover - fallback for direct execution
    from checker import analyze_and_sign, analyze_file, annotate_pdf, ensure_keypair

__all__ = ["analyze_and_sign", "analyze_file", "annotate_pdf", "ensure_keypair"]
