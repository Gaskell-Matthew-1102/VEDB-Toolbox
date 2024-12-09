# This testing code was written by Matthew. For full credit information please consult conftest.py

import pytest
import os
import pandas as pd
from flaskr.visualizer import setup, get_video_width, get_video_duration, get_video_height, parse_pldata, read_pldata

# For these three tests, I am using video file 421425-eye1.mp4 (https://nyu.databrary.org/volume/1612/slot/65967/-?asset=443360)
# added some error checking if tests ran w/o file (test_video_length throws div by 0 error when not supplied a proper file)
def test_video_width():
    video_file = "421435-eye1.mp4"
    if os.path.exists(video_file):
        assert get_video_width(video_file) == 400
    else:
        assert get_video_width(video_file) == 0.0

def test_video_height():
    video_file = "421435-eye1.mp4"
    if os.path.exists(video_file):
        assert get_video_height(video_file) == 400
    else:
        assert get_video_height(video_file) == 0.0

def test_video_length():
    video_file = "421435-eye1.mp4"
    if os.path.exists(video_file):
        assert get_video_duration(video_file) == 746.6416666666667

# For this test I am using the odometry.pldata file found at https://osf.io/gr42e
# This is a test to ensure that all data exists after reading and parsing
# As before, added error checking if file is not present
def test_pldata_parsing():
    pl_file = "odometry.pldata"
    if os.path.exists(pl_file):
        read_data = read_pldata(pl_file)
        df = pd.DataFrame(read_data)
        parsed_data = parse_pldata(pd.DataFrame(read_data)[1].iloc[0])
        assert parsed_data['topic'] == 'odometry'
        assert parsed_data['timestamp'] == 3311.823174577
        assert parsed_data['source_timestamp'] == 1615929523.6848683
        assert parsed_data['tracker_confidence'] == 2
        assert parsed_data['position_0'] == 0.0
        assert parsed_data['position_1'] == 0.0
        assert parsed_data['position_2'] == 0.0
        assert parsed_data['orientation_0'] == 0.9942581057548523
        assert parsed_data['orientation_1'] == 0.09853336215019226
        assert parsed_data['orientation_2'] == -0.007079203613102436
        assert parsed_data['orientation_3'] == -0.041133057326078415
        assert parsed_data['linear_velocity_0'] == 0.0
        assert parsed_data['linear_velocity_1'] == 0.0
        assert parsed_data['linear_velocity_2'] == 0.0
        assert parsed_data['angular_velocity_0'] == -0.06735000014305115
        assert parsed_data['angular_velocity_1'] == -0.06243877857923508
        assert parsed_data['angular_velocity_2'] == -0.06269194185733795
        assert parsed_data['linear_acceleration_0'] == 0.0
        assert parsed_data['linear_acceleration_1'] == 0.0
        assert parsed_data['linear_acceleration_2'] == 0.0
        assert parsed_data['angular_acceleration_0'] == -1.409101963043213
        assert parsed_data['angular_acceleration_1'] == -1.409101963043213
        assert parsed_data['angular_acceleration_2'] == 1.3732579946517944
    else:
        assert True