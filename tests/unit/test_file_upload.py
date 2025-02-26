# This testing code was written by Matthew. For full credit information please consult conftest.py

import pytest
import flaskr.file_upload
from flaskr.file_upload import app, validate_link, validate_video_files, validate_data_files, set_failed_upload, \
    set_failed_link, reset_failures, failed_data_upload, failed_video_link, failed_data_link, failed_video_upload
from flaskr.folder_upload import validate_video_path, validate_data_path

def test_validate_link():
    assert not validate_link('falselink.com', 1)
    assert not validate_link('falselink.com', 0)
    assert validate_link('https://nyu.databrary.org/volume/1612/slot/65955/-', 0)
    assert validate_link('https://osf.io/6m2ak/download', 1)

def test_validate_video_files():
    #just checks for 3 mp4 videos and 1 csv file
    video_list = ["video1.mp4", "video2.mp4"]
    assert not validate_video_files(video_list)
    video_list.append("video3.mp4")
    assert not validate_video_files(video_list)
    video_list.append("excsv.csv")
    assert not validate_video_files(video_list)
    video_list.clear()
    video_list = ["eye0.mp4", "eye1.mp4", "worldPrivate.mp4", "example.csv"]
    assert validate_video_files(video_list)

def test_validate_data_files():
    #15 random files (first check is file count)
    data_list = ["file1.txt", "file2.txt", "file3.txt", "file4.txt", "file5.txt"
                 "file6.txt", "file7.txt", "file8.txt", "file9.txt", "file10.txt"
                 "file11.txt", "file12.txt", "file13.txt", "file14.txt", "file15.txt"]
    assert not validate_data_files(data_list)
    #15 specific files (second check checks for these)
    data_list = ["eye0_timestamps.npy", "eye0.pldata", "eye1_timestamps.npy", "eye1.pldata",
                      "accel_timestamps.npy", "accel.pldata", "gyro_timestamps.npy", "gyro.pldata",
                      "odometry_timestamps.npy", "odometry.pldata", "world.intrinsics", "world.extrinsics",
                        "world_timestamps.npy", "marker_times.yaml", "world.pldata"]
    assert validate_data_files(data_list)

# This uses file paths from my own machine, edit if running this test elsewhere
def test_validate_paths():
    vpath = "C:\\Users\mattg\Downloads\VEDB Toolbox Test Files\\65967-2021_03_16_17_18_42"
    dpath = "C:\\Users\mattg\Downloads\VEDB Toolbox Test Files\\2021_03_16_17_18_42"
    assert validate_video_path(vpath)
    assert validate_data_path(dpath)