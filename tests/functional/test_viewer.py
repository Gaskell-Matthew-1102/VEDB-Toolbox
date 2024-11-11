from flaskr.visualizer import app

def test_three_videos():
    response = app.test_client().get("/visualizer")
    assert response.status_code == 200
    assert b'../static/worldvideo.mp4' in response.data
    assert b'../static/eye0.mp4' in response.data
    assert b'../static/eye1.mp4' in response.data