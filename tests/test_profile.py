import pytest
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

# Note: These tests will require a logged-in user.
# You would typically handle this by creating a user and logging them in within the test setup.

def test_update_profile(client):
    """Test updating a user's profile."""
    # This is a placeholder for a test that requires a logged-in user.
    # You would first log in a user, then post to /modifier_profil
    pass

def test_delete_account(client):
    """Test deleting a user account."""
    # This is a placeholder for a test that requires a logged-in user.
    # You would first log in a user, then post to /supprimer_compte
    pass
