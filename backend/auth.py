"""Compatibility entrypoint for the Flask app."""
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import create_app  # pylint: disable=wrong-import-position
from backend.ca import generate_certificate  # pylint: disable=wrong-import-position
from backend.users import load_users  # pylint: disable=wrong-import-position

app = create_app()

__all__ = ["app", "load_users", "generate_certificate"]


if __name__ == "__main__":
    app.run(debug=False)
