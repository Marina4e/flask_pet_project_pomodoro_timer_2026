from __future__ import annotations

from app import create_app


def test_create_app_uses_testing_config():
    app = create_app("testing")

    assert app.config["TESTING"] is True
    assert app.config["ENV_NAME"] == "testing"


def test_routes_are_registered(app):
    routes = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/" in routes
    assert "/calendar" in routes
    assert "/statistics" in routes
    assert "/api/docs" in routes
    assert "/api/health" in routes
