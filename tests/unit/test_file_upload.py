import pytest
import flaskr.file_upload
from flaskr.file_upload import app, validate_link, validate_video_files, validate_data_files

def test_file_upload_initial_route():
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert b"File Upload" in response.data
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
    #Item 1 is the help section for video files
    assert b"item-1" in response.data
    #Item 2 is the help section for data files
    assert b"item-2" in response.data

def test_validate_link():
    assert not validate_link('falselink.com', 1)
    assert not validate_link('falselink.com', 0)
    assert validate_link('https://nyu.databrary.org/volume/1612/slot/65955/-', 0)
    assert validate_link('https://osf.io/6m2ak/download', 1)

def test_validate_video_files():
    video_list = ["video1.mp4", "video2.mp4"]
    assert not validate_video_files(video_list)
    video_list.append("video3.mp4")
    assert not validate_video_files(video_list)
    video_list.append("excsv.csv")
    assert validate_video_files(video_list)
    video_list.pop()
    assert not validate_video_files(video_list)

def test_validate_data_files():
    #15 random files (first check is file count)
    data_list = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt"
                 "file6.txt", "file7.txt", "file8.txt", "file9.txt", "file10.txt"
                 "file11.txt", "file12.txt", "file13.txt", "file14.txt", "file15.txt"]
    assert not validate_data_files(data_list)
    #15 specific files (second check checks for these)
    data_list = ["eye0_timestamps.npy", "eye0.pldata", "eye1_timestamps.npy", "eye1.pldata",
                      "accel_timestamps.npy", "accel.pldata", "gyro_timestamps.npy", "gyro.pldata",
                      "odometry_timestamps.npy", "odometry.pldata", "world.intrincics", "world.extrincics",
                        "world_timestamps.npy", "marker_times.yaml", "world.pldata"]
    assert validate_data_files(data_list)
    #1 file missing should invalidate the function
    data_list.pop()
    assert not validate_data_files(data_list)