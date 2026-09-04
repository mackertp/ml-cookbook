"""Flask integration helpers for prm-studio.

@author: Preston Mackert
"""

from __future__ import annotations

from flask import Blueprint, Flask


def create_prm_studio_blueprint() -> Blueprint:
    """Build the design-system blueprint with packaged static and templates."""
    return Blueprint(
        "prm_studio",
        __name__,
        static_folder="static",
        static_url_path="/prm-studio/static",
        template_folder="templates",
    )


def register_prm_studio(app: Flask) -> None:
    """Register prm-studio once on a Flask application."""
    if "prm_studio" in app.blueprints:
        return
    app.register_blueprint(create_prm_studio_blueprint())
