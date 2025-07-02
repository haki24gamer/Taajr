import pytest
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

# Note: These tests will require a logged-in seller user.
# You would typically handle this by creating a user and logging them in within the test setup.

def test_add_offer(client):
    """Test adding a new offer."""
    # This is a placeholder for a test that requires a logged-in seller.
    # You would first log in a seller, then post to /ajouter_offre
    pass

def test_edit_offer(client):
    """Test editing an existing offer."""
    # This is a placeholder for a test that requires a logged-in seller.
    # You would first log in a seller, then post to /modifier_offre
    pass

def test_delete_offer(client):
    """Test deleting an offer."""
    # This is a placeholder for a test that requires a logged-in seller.
    # You would first log in a seller, then post to /supprimer_offre/<offre_id>
    pass
