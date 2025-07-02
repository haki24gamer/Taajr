import pytest
from app import app as flask_app, mail
from flask import session

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_inscription_admin_sends_email(client, mocker):
    """Test that the /Inscription_Admin route sends an email."""
    # Mock the mail.send method
    mock_send = mocker.patch('flask_mail.Mail.send')

    with client.session_transaction() as sess:
        sess['_flashes'] = []

    # Simulate a POST request to the /Inscription_Admin route
    response = client.post('/Inscription_Admin', data={
        'adminName': 'test',
        'adminFirstName': 'user',
        'adminEmail': 'test@example.com',
        'adminPassword': 'password',
        'adminPhone': '77123456',
        'adminBirthDate': '2000-01-01',
        'adminGender': 'Homme'
    })

    # Check that the mail.send method was called once
    assert mock_send.called
    assert mock_send.call_count == 1

    # Check that the response is a redirect to the OTP verification page
    assert response.status_code == 302
    assert response.location == '/verify_otp'
