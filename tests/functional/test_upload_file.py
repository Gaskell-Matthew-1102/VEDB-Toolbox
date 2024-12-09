# This testing code was written by Matthew. For full credit information please consult conftest.py

from flaskr.file_upload import get_showform
from tests.conftest import test_client

# Tests the file upload page's visibility
def test_file_help_route(test_client):
    response = test_client.get('/upload_help')
    assert response.status_code == 200
    #Title
    assert b"How To Upload Files" in response.data
    #Infoblock 1 is the help section for video files
    assert b"infoblock1" in response.data
    #Infoblock 2 is the help section for data files
    assert b"infoblock2" in response.data

# Tests the return from file upload help back to file upload
def test_back_to_upload(test_client):
    response = test_client.post('/go_back')
    assert response.status_code == 200
    assert b"Upload Files" in response.data
    assert b'<form action = "/upload_video" method="POST" enctype="multipart/form-data">' in response.data
    assert b'<form action = "/upload_data" method="POST" enctype="multipart/form-data">' in response.data
    assert b'<form action = "/upload_video_link" method="POST" enctype="multipart/form-data">' in response.data
    assert b'<form action = "/upload_data_link" method="POST" enctype="multipart/form-data">' in response.data

# Tests the upload different video button
def test_upload_different_video(test_client):
    response = test_client.get('/upload_different_video')
    assert response.status_code == 405
    response = test_client.post('/upload_different_video')
    assert response.status_code == 200
    assert get_showform(1) is True
    assert b'<form action = "/upload_video" method="POST" enctype="multipart/form-data">' in response.data

# Tests the upload different data button
def test_upload_different_data(test_client):
    response = test_client.get('/upload_different_data')
    assert response.status_code == 405
    response = test_client.post('/upload_different_data')
    assert response.status_code == 200
    assert get_showform(2) is True
    assert b'<form action = "/upload_data" method="POST" enctype="multipart/form-data">' in response.data

# Tests the responses when incorrect links are posted into the upload link forms
def test_bad_link_input(test_client):
    # Bad video link
    response = test_client.post('/upload_video_link', data=dict(video_link='test.com'))
    assert response.status_code == 200
    assert b'Success' not in response.data
    assert (b'Incorrect video link uploaded. Either the link was invalid or the files could not be downloaded. '
            b'Please try again, or refer to the link below for help.') in response.data

    # Bad data link
    response = test_client.post('/upload_data_link', data=dict(data_link='different_test.com',))
    assert response.status_code == 200
    assert b'Success' not in response.data
    assert (b'Incorrect data link uploaded. Either the link was invalid or the files could not be downloaded. '
            b'Please try again, or refer to the link below for help.') in response.data

    # Quick test to ensure the reset_failures() function works (failure messages should go away on different action)
    response = test_client.get('/upload_help')
    assert response.status_code == 200
    response = test_client.post('/go_back')
    assert response.status_code == 200
    assert (b'Incorrect data link uploaded. Either the link was invalid or the files could not be downloaded. '
            b'Please try again, or refer to the link below for help.') not in response.data

# This tests the file upload buttons, and the errors that happen when incorrect files are uploaded
def test_bad_file_input(test_client):
    # Bad video file list
    response = test_client.post('/upload_video', data=dict(file='[odometry.py]'))
    assert response.status_code == 200
    assert b'Success' not in response.data
    assert b'Incorrect video files uploaded. Please try again, or refer to the link below for help.' in response.data

    # Bad data file list
    response = test_client.post('/upload_data', data=dict(file='[odometry.pldata]'))
    assert response.status_code == 200
    assert b'Success' not in response.data
    assert b'Incorrect data files uploaded. Please try again, or refer to the link below for help.' in response.data

    # Quick test to ensure the reset_failures() function works (failure messages should go away on different action)
    response = test_client.get('/upload_help')
    assert response.status_code == 200
    response = test_client.post('/go_back')
    assert response.status_code == 200
    assert b'Incorrect data files uploaded. Please try again, or refer to the link below for help.' not in response.data