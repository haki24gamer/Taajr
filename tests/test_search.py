import pytest
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_search_product(client):
    """Test searching for a product."""
    response = client.get('/search?query=test&category=produit')
    assert response.status_code == 200

def test_search_service(client):
    """Test searching for a service."""
    response = client.get('/search?query=test&category=service')
    assert response.status_code == 200

def test_search_boutique(client):
    """Test searching for a boutique."""
    response = client.get('/search?query=test&category=boutique')
    assert response.status_code == 200

def test_search_category(client):
    """Test searching for a category."""
    response = client.get('/search?query=test&category=categorie')
    assert response.status_code == 200
