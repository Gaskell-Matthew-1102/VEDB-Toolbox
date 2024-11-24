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

# This function will run when a user chooses to log out, NEEDS CODE TO RETURN TO LOGIN SCREEN
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
    print("here")
    graphing()

    # setup()
    # return render_template("visualizer/visualizer.html", video_height=video_height, video_width=video_width,
    #                        worldvideo_filename=worldvideo_filename)

# The following two functions were provided to us by Brian Szekely, a UNR PhD student and a former student
# of Paul MacNeilage's Self Motion Lab
def read_pldata(path):
    with open(path, 'rb') as file:
        unpacker = msgpack.Unpacker(file, raw=False)
        data = []
        for packet in unpacker:
            data.append(packet)
    return data

def parse_pldata(data):
    unpacker = msgpack.Unpacker(io.BytesIO(data), raw=False)
    parsed_data = next(unpacker)

    flattened = {}
    for key, value in parsed_data.items():
        if isinstance(value, list):
            for i, item in enumerate(value):
                flattened[f"{key}_{i}"] = item
        else:
            flattened[key] = value

    return flattened

def graphing():
    # if get_is_folder(2):
    #     path = "flaskr/" + data_folder_name + "/odometry.pldata"
    #     odometry_data = read_pldata(path)
    # else:
    #     odometry_data = read_pldata("flaskr/odometry.pldata")

    odometry_data = read_pldata("odometry.pldata")

    df = pd.DataFrame(odometry_data)
    parsed_data = parse_pldata(pd.DataFrame(odometry_data)[1].iloc[0])
    list_all = []
    for i in range(len(df)):
        list_all.append(parse_pldata(df[1].iloc[0]))

    print(parsed_data)

    # fig = px.line(list_all, x='timestamp', y='position_0')
    # fig.write_image("odometry.png")
    # fig.show(renderer="png")

if __name__ == "__main__":
    main()