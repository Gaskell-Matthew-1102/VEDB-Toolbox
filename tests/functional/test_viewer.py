# This testing code was written by Matthew. For full credit information please consult conftest.py

from tests.conftest import *
from flaskr.file_upload import set_showform
import os

def test_three_videos(test_client):
    set_showform(1, False)
    set_showform(2, False)
    response = test_client.post("/visualizer")
    assert response.status_code == 200
    assert b'../static/worldvideo.mp4' in response.data
    assert b'../static/eye0.mp4' in response.data
    assert b'../static/eye1.mp4' in response.data

def test_button_appearance(test_client):
    response = test_client.post("/visualizer")
    assert response.status_code == 200
    assert b'<button onclick="skip_10_backward()">Backward 10 Sec</button>' in response.data
    assert b'<button onclick="play_pause()">Play/Pause</button>' in response.data
    assert b'<button onclick="stop_video()">Stop</button>' in response.data
    assert b'<button onclick="skip_10_forward()">Forward 10 Sec</button>' in response.data

#WRITE A TEST GRAPH APPEARANCE

def test_exit_viewer(test_client):
    response = test_client.post("/exit_visualizer")
    assert response.status_code == 200
    assert b"Upload Files" in response.data
    assert b'<button onclick="skip_10_backward()">Backward 10 Sec</button>' not in response.data
    assert b'<button onclick="play_pause()">Play/Pause</button>' not in response.data
    assert b'<button onclick="stop_video()">Stop</button>' not in response.data
    assert b'<button onclick="skip_10_forward()">Forward 10 Sec</button>' not in response.data
    if os.path.exists('linear_velocity_graph.png'):
        os.remove('linear_velocity_graph.png')
    if os.path.exists('linear_acceleration_graph.png'):
        os.remove('linear_acceleration_graph.png')