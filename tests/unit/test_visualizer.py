import pytest
import os

from flaskr.visualizer import setup, get_video_width, get_video_duration, get_video_height

#For these three tests, I am using video file 421425-eye1.mp4 (https://nyu.databrary.org/volume/1612/slot/65967/-?asset=443360)
#added some error checking if tests ran w/o file (test_video_length throws div by 0 error when not supplied a proper file)
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