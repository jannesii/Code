"""Auth blueprint package."""

try:
    from .routes import auth_bp  # noqa: F401
except Exception:
    auth_bp = None  # type: ignore

