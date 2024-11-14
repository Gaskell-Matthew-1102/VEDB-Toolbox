from flaskr.visualizer import app

def test_three_videos():
    response = app.test_client().get("/visualizer")
    assert response.status_code == 200
    assert b'../static/worldvideo.mp4' in response.data
    assert b'../static/eye0.mp4' in response.data
    assert b'../static/eye1.mp4' in response.data

def test_button_appearance():
    response = app.test_client().get("/visualizer")
    assert response.status_code == 200
    assert b'<button onclick="skip_10_backward()">Backward 10 Sec</button>' in response.data
    assert b'<button onclick="play_pause()">Play/Pause</button>' in response.data
    assert b'<button onclick="stop_video()">Stop</button>' in response.data
    assert b'<button onclick="skip_10_forward()">Forward 10 Sec</button>' in response.data

def test_upload_new_files():
    response = app.test_client().get("/new_files")
    assert response.status_code == 405
    # response = app.test_client().post("/new_files")
    # assert response.status_code == 200
    # assert b"File Upload" in response.data