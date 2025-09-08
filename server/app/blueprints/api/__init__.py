"""API blueprint package."""

# Re-export for convenient import as app.blueprints.api
try:
    from .routes import api_bp  # noqa: F401
except Exception:
    # During refactor, routes may not exist yet
    api_bp = None  # type: ignore

