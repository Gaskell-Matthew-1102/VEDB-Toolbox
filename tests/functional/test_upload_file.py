import pytest
import os
from flaskr import create_app
import flaskr.file_upload
from flaskr.file_upload import app, validate_link, validate_video_files, validate_data_files, get_showform


# from flaskr.visualizer import data_list


def test_file_upload_initial_route():
    #This will probably be used when we link together all the files
    #os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    #app = create_app('testing')
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert b"Upload Files" in response.data
    #Form to upload video files
    assert b'<form action = "/upload_video" method="POST" enctype="multipart/form-data">' in response.data
    #Form to upload data files
    assert b'<form action = "/upload_data" method="POST" enctype="multipart/form-data">' in response.data
    #Form to paste link for download of video files
    assert b'<form action = "/upload_video_link" method="POST" enctype="multipart/form-data">' in response.data
    #Form to paste link for download of data files
    assert b'<form action = "/upload_data_link" method="POST" enctype="multipart/form-data">' in response.data

def test_file_help_route():
    response = app.test_client().get('/upload_help')
    assert response.status_code == 200
    #Title
    assert b"How To Upload Files" in response.data
    #Infoblock 1 is the help section for video files
    assert b"infoblock1" in response.data
    #Infoblock 2 is the help section for data files
    assert b"infoblock2" in response.data

def test_back_to_upload():
    response = app.test_client().post('/go_back')
    assert response.status_code == 200
    assert b"Upload Files" in response.data
    assert b'<form action = "/upload_video" method="POST" enctype="multipart/form-data">' in response.data
    assert b'<form action = "/upload_data" method="POST" enctype="multipart/form-data">' in response.data
    assert b'<form action = "/upload_video_link" method="POST" enctype="multipart/form-data">' in response.data
    assert b'<form action = "/upload_data_link" method="POST" enctype="multipart/form-data">' in response.data

def test_upload_different_video():
    response = app.test_client().get('/upload_different_video')
    assert response.status_code == 405
    response = app.test_client().post('/upload_different_video')
    assert response.status_code == 200
    assert get_showform(1) is True
    assert b'<form action = "/upload_video" method="POST" enctype="multipart/form-data">' in response.data

def test_upload_different_data():
    response = app.test_client().get('/upload_different_data')
    assert response.status_code == 405
    response = app.test_client().post('/upload_different_data')
    assert response.status_code == 200
    assert get_showform(2) is True
    assert b'<form action = "/upload_data" method="POST" enctype="multipart/form-data">' in response.data