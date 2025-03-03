# i would like to thank chatgpt for giving the initial push and fixing the db issues.
# would like to say this is mainly my work tho
# move to directory root? not sure why this is needed
# run with pytest ./test_user_creation.py

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.security import generate_password_hash

from flaskr import create_app
from flaskr.models import db, Users

@pytest.fixture
def app() -> Flask:
    """Create and configure a new app instance for each test."""
    app = create_app(test_config=True)
    with app.app_context():
        db.create_all()  # Create the database tables
    yield app
    with app.app_context():
        db.drop_all()  # Drop the database tables after tests
        db.session.remove()  # Remove any session state

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Fixture to provide a test client."""
    client = app.test_client()

    # Before each test, start a new transaction
    with app.app_context():
        db.session.begin()  # Begin a transaction

    yield client

    # After each test, rollback the transaction to undo any changes
    with app.app_context():
        db.session.rollback()  # Rollback the transaction to undo changes

def test_successful_user_creation(client: FlaskClient):
    """Test user creation with valid data."""
    # Simulate a POST request to the registration form with valid data
    response = client.post('/landing', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'testpassword',
        'repeat_password': 'testpassword',
        'recaptcha': 'dummy-captcha-response',
        'submit': 'Submit'
    })

    # Check if the user is redirected to the home page (successful login)
    assert response.status_code == 302  # Redirect after successful registration
    assert Users.query.filter_by(username='newuser').first() is not None  # User exists in DB

def test_unsuccessful_creation_due_to_mismatched_passwords(client: FlaskClient):
    """Test user creation where the passwords do not match."""
    # Simulate a POST request to the registration form with mismatched passwords
    response = client.post('/landing', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'testpassword',
        'repeat_password': 'differentpassword',
        'recaptcha': 'dummy-captcha-response',
        'submit': 'Submit'
    })

    # Check if the form renders again with a flash message
    assert response.status_code == 200  # Should stay on the same page
    assert Users.query.filter_by(username='newuser').first() is None  # User should not exist in DB

def test_unsuccessful_creation_due_to_existing_username(client: FlaskClient):
    """Test user creation where the username is already taken."""
    # Create an existing user in the database
    existing_user = Users(username='existinguser', email='existing@example.com', password=generate_password_hash('password'))
    db.session.add(existing_user)
    db.session.commit()

    # Simulate a POST request to the registration form with a duplicate username
    response = client.post('/landing', data={
        'username': 'existinguser',
        'email': 'newemail@example.com',
        'password': 'testpassword',
        'repeat_password': 'testpassword',
        'recaptcha': 'dummy-captcha-response',
        'submit': 'Submit'
    })

    # Check if the form renders again with a flash message
    assert response.status_code == 200  # Should stay on the same page
    assert Users.query.filter_by(username='existinguser').count() == 1  # Only one user should exist
