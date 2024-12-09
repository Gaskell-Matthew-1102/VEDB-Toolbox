# This testing code was written by Matthew. For full credit information please consult conftest.py

from flaskr.models import Users
from werkzeug.security import generate_password_hash
from tests.conftest import new_test_user

def test_new_user():
    user = Users(username='testuser', email='testemail@test.com', password=generate_password_hash('testpassword'), administrator=False)
    assert user.username == 'testuser'
    assert user.email == 'testemail@test.com'
    assert user.password != 'testpassword'
    assert user.is_authenticated
    assert user.is_active
    assert user.administrator is False
    assert not user.is_anonymous

def test_new_user_fixture(new_test_user):
    assert new_test_user.username == 'example'
    assert new_test_user.email == 'user@email.com'
    assert new_test_user.password != 'password'
    assert new_test_user.administrator is True
    assert new_test_user.is_authenticated
    assert new_test_user.is_active
    assert not new_test_user.is_anonymous