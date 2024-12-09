# All of the code in this file was our own work, apart from dimension code, which has been cited below

import io
import msgpack
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from flaskr import file_upload
from flaskr.file_upload import *

import cv2
app = Flask(__name__)

#Global variables for the list of video files and data files
video_list = []
data_list = []

#If data was passed in through the upload link feature
video_folder = ""
data_folder = ""

#Global variables for video file names (not named by convention)
eye0_filename = ""
eye1_filename = ""
worldvideo_filename = ""
csvfilename = ""

#Initializing variables function, takes in information from file_upload
def setup() -> bool:
    global video_list
    video_list = file_upload.get_video_list()
    global data_list
    data_list = file_upload.get_data_file_list()

    global video_folder
    video_folder = file_upload.get_folder_name(1)
    global data_folder
    data_folder = file_upload.get_folder_name(2)

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

#Sourced dimension code from here https://stackoverflow.com/questions/7348505/get-dimensions-of-a-video-file
def get_video_height(vid_file):
    video_file = cv2.VideoCapture(vid_file)
    height = video_file.get(cv2.CAP_PROP_FRAME_HEIGHT)
    video_file.release()
    return height

def get_video_width(vid_file):
    video_file = cv2.VideoCapture(vid_file)
    width = video_file.get(cv2.CAP_PROP_FRAME_WIDTH)
    video_file.release()
    return width

def get_video_duration(vid_file):
    video_file = cv2.VideoCapture(vid_file)
    frame_rate = video_file.get(cv2.CAP_PROP_FPS)
    frames = video_file.get(cv2.CAP_PROP_FRAME_COUNT)
    video_file.release()
    length = frames/frame_rate
    return length

#This function will run when user presses the Exit Visualizer button, returns to file upload with state of files saved
def exit_visualizer():
    if request.method == "POST":
        show_form_video = get_showform(1)
        show_form_data = get_showform(2)
        return render_template("file-upload/file_upload.html", show_form1=show_form_video, show_form2=show_form_data)

# This function will run when a user chooses to log out, NEEDS CODE TO RETURN TO LOG IN SCREEN
@app.route("/visualizer_logout", methods=["POST"])
def logout() -> None:
    if request.method == "POST":
        #once again code likely here to end/clsoe video playback, other file uses

        file_upload.delete_files_in_list(video_list)
        file_upload.delete_files_in_list(data_list)
        if file_upload.get_is_folder(1):
            name_folder = file_upload.get_folder_name(1)
            shutil.rmtree(name_folder)
        if file_upload.get_is_folder(2):
            name_folder = file_upload.get_folder_name(2)
            shutil.rmtree(name_folder)
            shutil.rmtree("__MACOSX")
        #some code here to run logout functionality

def main():
    setup()
    # return render_template("visualizer/visualizer.html", video_height=video_height, video_width=video_width,
    #                        worldvideo_filename=worldvideo_filename)

if __name__ == "__main__":
    main()