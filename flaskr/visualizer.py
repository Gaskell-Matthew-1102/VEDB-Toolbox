from flask import *
import os

import file_upload
from flaskr.file_upload import get_video_list, get_data_file_list, delete_files_in_list

app = Flask(__name__)

#Global variables for the list of video files and data files
video_list = []
data_list = []

#Global variables for video file names (not named by convention)
eye0_filename = ""
eye1_filename = ""
worldvideo_filename = ""
csvfilename = ""

#Initializing variables function, takes in information from file_upload
def setup() -> bool:
    global video_list
    video_list = get_video_list()
    global data_list
    data_list = get_data_file_list()

    global eye0_filename
    global eye1_filename
    global worldvideo_filename
    global csvfilename

    for filename in video_list:
        if "eye0" in filename:
            eye0_filename = filename
        elif "eye1" in filename:
            eye1_filename = filename
        elif "world" in filename:
            worldvideo_filename = filename
        elif ".csv" in filename:
            csvfilename = filename
        else:
            #should never hit this, but extra edge case checking can't hurt
            return False

    return True

#This function will run when user presses an Upload New Files button, removes current files, returns to file upload screen
@app.route("/new_files", methods=["POST"])
def upload_new_files() -> None:
    if request.method == "POST":
        #code here likely to end/close video playback, anything that is using a file

        delete_files_in_list(video_list)
        delete_files_in_list(data_list)
        file_upload.main()

@app.route("/visualizer")
def main():
    # if setup():
    #     render_template("templates/visualizer/main.html")
    return render_template("visualizer/main.html")

if __name__ == "__main__":
    app.run(debug=True)