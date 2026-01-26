"""Entry point for running the Plag Checker app."""
from backend.app import create_app


def main():
    """Run the Flask development server."""
    app = create_app()
    app.run(debug=False)


if __name__ == "__main__":
    main()
