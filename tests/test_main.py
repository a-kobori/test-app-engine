"""Tests for main Flask application."""
import pytest
from todo_app.main import create_app


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_index_page(client):
    """Test main index page."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"TODO App" in response.data
    assert b"test@example.com" in response.data


def test_create_app():
    """Test application factory."""
    app = create_app()
    assert app is not None
    assert app.name == "todo_app.main"