#Accidentally nuked during fixes, copy back from P3 doc
#test_admin_dash.py
from werkzeug.security import generate_password_hash
from flaskr.models import Users
from flaskr.search import searchBar


def test_admin_search_user(init_database):
    testuser = Users(username='ack', email='test@unr.edu', password=generate_password_hash('testpassword'), administrator=True)
    #User "ack" exists in the db, so search key "a"
    #sgould yield a result
    list_result = searchBar("a", "username")
    assert list_result is not None
    assert list_result[0][0] == testuser.username
    assert list_result[0][1] == testuser.email
    assert list_result[0][2] == testuser.administrator

    #Similarly, searching by a key that
    #no user has should yield no results
    list_result = searchBar("nonExistentSubstring", "username")
    assert list_result == []

    #And then searching by email should work
    list_result = searchBar(".edu", "email")
    assert list_result is not None
    assert list_result[0][0] == testuser.username
    assert list_result[0][1] == testuser.email
    assert list_result[0][2] == testuser.administrator