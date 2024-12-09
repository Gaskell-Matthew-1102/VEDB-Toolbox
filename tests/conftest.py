# This testing configuration file was written by Matthew
# Additionally, Matthew wrote all the other tests contained in the functional folder (test_login.py, test_upload_file.py,
# test_viewer.py) and in the unit folder (test_file_upload.py, test_models.py, test_visualizer.py)
# When writing a lot of this testing code (mainly configuration, but also some of the other tests) I referenced this resource
# for some assistance: https://testdriven.io/blog/flask-pytest/

import os
import pytest
from werkzeug.security import generate_password_hash

from flaskr.models import Users
from flaskr import create_app, db

@pytest.fixture(scope='module')
def new_test_user():
    user = Users(username='example', email='user@email.com', password=generate_password_hash('password'), administrator=True)
    return user

@pytest.fixture(scope='module')
def test_client():
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    with flask_app.test_client() as test_client:
        with flask_app.app_context():
            yield test_client

@pytest.fixture(scope='module')
def init_database(test_client, new_test_user):
    db.create_all()
    default_user = Users(username='test', email='test@unr.edu', password='password', administrator=True)
    db.session.add(default_user)
    db.session.commit()
    yield
    db.drop_all()

@pytest.fixture(scope='module')
def test_login(test_client):
    test_client.post('/login', data={'username': 'test', 'password': 'password'})
    yield
    test_client.get('/logout')