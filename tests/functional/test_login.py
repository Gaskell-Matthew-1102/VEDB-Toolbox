# This testing code was written by Matthew. For full credit information please consult conftest.py

from tests.conftest import *

# Base test to assure that login site is visible initially
def test_login_site(test_client):
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'<div class="flex-container" id="login-panel">' in response.data
    assert b'<button type="button" id="button-div">Register</button>' in response.data

# This test runs through logging in a user, where that follows to, then logging out and where that goes
def test_user_login_logout(test_client, init_database):
    # Fix this to work with WTForms
    response = test_client.post('/login', data=dict(username='test', password='password'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Upload Files" in response.data
    assert b'<form action = "/upload_video" method="POST" enctype="multipart/form-data">' in response.data
    assert b'<form action = "/upload_data" method="POST" enctype="multipart/form-data">' in response.data
    assert b'<form action = "/upload_video_link" method="POST" enctype="multipart/form-data">' in response.data
    assert b'<form action = "/upload_data_link" method="POST" enctype="multipart/form-data">' in response.data

    # This should work
    response = test_client.get('/logout')
    assert response.status_code == 200
    assert b'<div class="flex-container" id="login-panel">' in response.data
    assert b'<button type="button" id="button-div">Register</button>' in response.data

# Attempts to log in with unauthorized credentials, tests that it does not follow a path and stays on the login screen
def test_unauthorized_login(test_client, init_database):
    response = test_client.post('/login', data=dict(username='incorrect', password='wrong'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Upload Files" not in response.data
    assert b'<form action = "/upload_video" method="POST" enctype="multipart/form-data">' not in response.data
    assert b'<div class="flex-container" id="login-panel">' in response.data
    assert b'<button type="button" id="button-div">Register</button>' in response.data