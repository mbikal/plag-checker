"""Entry point for running the Plag Checker app."""
from backend.auth import app


def main():
    """Run the Flask development server."""
    app.run(debug=False)


if __name__ == "__main__":
    main()
