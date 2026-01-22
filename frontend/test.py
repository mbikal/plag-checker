"""
Lightweight sanity checks for the frontend structure.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_contains(path: Path, needle: str) -> None:
    content = read_text(path)
    if needle not in content:
        raise AssertionError(f"Expected '{needle}' in {path}")


def test_required_files_exist() -> None:
    required = [
        SRC / "App.tsx",
        SRC / "routes.tsx",
        SRC / "pages" / "HomePage.tsx",
        SRC / "pages" / "AuthPage.tsx",
        SRC / "pages" / "UploadPage.tsx",
        SRC / "assets" / "report.svg",
        SRC / "assets" / "scan.svg",
        SRC / "assets" / "library.svg",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        raise AssertionError(f"Missing frontend files: {', '.join(str(p) for p in missing)}")


def test_routes_defined() -> None:
    routes_file = SRC / "routes.tsx"
    assert_contains(routes_file, "home:")
    assert_contains(routes_file, "auth:")
    assert_contains(routes_file, "upload:")


def test_app_routes_pages() -> None:
    app_file = SRC / "App.tsx"
    assert_contains(app_file, "HomePage")
    assert_contains(app_file, "AuthPage")
    assert_contains(app_file, "UploadPage")


if __name__ == "__main__":
    test_required_files_exist()
    test_routes_defined()
    test_app_routes_pages()
    print("frontend/test.py: ok")
