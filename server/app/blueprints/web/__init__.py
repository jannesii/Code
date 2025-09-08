"""Web (HTML) blueprint package."""

try:
    from .routes import web_bp  # noqa: F401
except Exception:
    web_bp = None  # type: ignore

