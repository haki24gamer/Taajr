import pytest
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_admin_routes_unauthorized(client):
    """Test that admin routes are inaccessible to unauthorized users."""
    admin_routes = [
        '/admin',
        '/gestion_utilisateurs',
        '/gestion_categories',
        '/gestion_commandes',
        '/gestion_messages',
        '/gestion_comptes_admin',
        '/gestion_offres'
    ]
    for route in admin_routes:
        response = client.get(route)
        assert response.status_code == 302  # Redirect to login

def test_vendeur_routes_unauthorized(client):
    """Test that vendeur routes are inaccessible to unauthorized users."""
    vendeur_routes = [
        '/offres_vendeurs',
        '/commandes_vendeurs'
    ]
    for route in vendeur_routes:
        response = client.get(route)
        assert response.status_code == 302  # Redirect to login
