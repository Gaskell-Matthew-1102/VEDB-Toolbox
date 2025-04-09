# All of the code in this file is our own, apart from some pldata functions, which have been credited below

import shutil

from flask import *
import atexit
import os
import numpy as np
#from pathlib import Path
import msgpack
#import collections
import pandas as pd
from io import BytesIO
import zipfile
import requests
import matplotlib.pyplot as plt
import math
import urllib
# from flaskr.fixation.fixation_packages.ingestion import parse_pldata, read_pldata

import plotly.graph_objects as go
from plotly import utils
from json import dumps

#Global variables
#File lists
video_file_list = []
data_file_list = []
graph_file_list = []

#Forms for file/link upload
show_form1 = True
show_form2 = True

#Failure variables (used in error message display within HTML)
failed_video_upload = False
failed_data_upload = False
failed_video_link = False
failed_data_link = False

#Extra folder variables (might not need these??)
are_videos_in_folder = False
is_data_in_folder = False

#Folder name variables (definitely need these)
video_folder_name = ""
data_folder_name = ""
processed_gaze_folder = ""

#FOR THE FOLLOWING GETTERS AND SETTERS: form_num is 1 for videos, 2 for data
def get_showform(form_num: int) -> int:
    if form_num == 1:
        return show_form1
    elif form_num == 2:
        return show_form2

def set_showform(form_num: int, flag: bool) -> None:
    if form_num == 1:
        global show_form1
        show_form1 = flag
    elif form_num == 2:
        global show_form2
        show_form2 = flag

# Setter for if an extra folder exists
def set_is_folder(form_num: int, flag: bool, name: str) -> None:
    if form_num == 1:
        global are_videos_in_folder
        are_videos_in_folder = flag
        global video_folder_name
        video_folder_name = name
    elif form_num == 2:
        global is_data_in_folder
        is_data_in_folder = flag
        global data_folder_name
        data_folder_name = name

# Getter for if an extra folder exists
def get_is_folder(form_num: int) -> bool:
    if form_num == 1:
        return are_videos_in_folder
    elif form_num == 2:
        return is_data_in_folder

# Failure setters
def set_failed_link(form_num: int, failed: bool) -> None:
    if form_num == 1:
        global failed_video_link
        failed_video_link = failed
    if form_num == 2:
        global failed_data_link
        failed_data_link = failed

def set_failed_upload(form_num: int, failed: bool) -> None:
    if form_num == 1:
        global failed_video_upload
        failed_video_upload = failed
    if form_num == 2:
        global failed_data_upload
        failed_data_upload = failed

# Used in navigations, gets rid of any error messages from failed uploads/downloads
def reset_failures():
    global failed_video_upload
    failed_video_upload = False
    global failed_data_upload
    failed_data_upload = False
    global failed_video_link
    failed_video_link = False
    global failed_data_link
    failed_data_link = False

#Two get functions for lists be utilized by the viewer application
def get_video_list() -> list:
    return video_file_list

def get_data_file_list() -> list:
    return data_file_list

def get_graph_file_list() -> list:
    return graph_file_list

# Used for the name of the folder holding video/data files when downloaded from a link
def get_folder_name(form_num: int) -> str:
    if form_num == 1:
        return video_folder_name
    elif form_num == 2:
        return data_folder_name

# Removes all files within a list passed in, does error checking first
def delete_files_in_list(listed_files) -> None:
    for file in listed_files:
        if os.path.isfile(file):
            os.remove(file)

def clear_lists():
    global video_file_list
    global data_file_list
    global graph_file_list
    video_file_list.clear()
    data_file_list.clear()
    graph_file_list.clear()

def delete_folders():
    if get_is_folder(1):
        flask_folder = "flaskr" + "\\" + get_folder_name(1)
        if os.path.exists(flask_folder):
            shutil.rmtree(flask_folder)
    if get_is_folder(2):
        flask_folder = "flaskr" + "\\" + get_folder_name(2)
        if os.path.exists(flask_folder):
            shutil.rmtree(flask_folder)
        mac_folder = "flaskr" + "\\" + "__MACOSX"
        if os.path.exists(mac_folder):
            shutil.rmtree(mac_folder)

#Automatically deletes populated files on exit of python program
#could add a feature where users choose to keep these files(??)
#If a link download was accomplished, deletes the folder created from that action
def delete_files_on_exit() -> None:
    for file in video_file_list:
        if os.path.isfile(file):
            os.remove(file)
    for file in data_file_list:
        if os.path.isfile(file):
            os.remove(file)
    for file in graph_file_list:
        if os.path.isfile(file):
            os.remove(file)
    delete_folders()

#This function validates that the link submitted is an actual link, and goes to the correct website w/ downloadable (can't really go further)
def validate_link(link: str, flag: int) -> bool:
    if "." not in link:
        return False
    if "osf.io" not in link and flag == 1:
        return False
    if "nyu.databrary.org" not in link and flag == 0:
        return False
    #Passes first check, still forced to hit others (exception)
    return True

# Downloads files from a given link
def download_from_url(link: str):
    response = requests.get(link)

    if response.status_code != 200:
        print(f"FAILED TO DOWNLOAD DATA FROM URL. STATUS CODE: {response.status_code}")
        raise Exception(f"Failed to download file: {response.status_code}")
    return response

# Downloads video files when presented with a Databrary link. The logic for downloading a file from this site is a little different, so a new function :)
def download_video_files(link: str):
    req = urllib.request.Request(link)
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7')
    req.add_header('referer', 'https://nyu.databrary.org/volume/1612/slot/65955/zip/false')
    req.add_header('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

    r = urllib.request.urlopen(req).read()
    return r

# The original code for this function was given to us by Brian Szekely, a PhD student and former student of
# Dr. MacNeilage's Self-Motion Lab. It has been slightly altered to fit our code.
# This function takes in a respinse from a GET response and unzips it
def extract_unzip(response) -> bool:
    zip_file = zipfile.ZipFile(BytesIO(response)) # get the zip file
    filepath = os.path.abspath(os.path.dirname( __file__ ))
    zip_file.extractall(filepath)
    return True

#This function validates that the files uploaded for videos are correct, some name checks some file ext. checks
def validate_video_files(file_list) -> bool:
    file_count = len(file_list)

    if file_count != 4:
        return False

    mp4_count = 0
    csv_count = 0

    for filename in file_list:
        file_type = filename.split(".", 1)[1]
        if file_type == 'mp4':
            if "eye0" in filename or "eye1" in filename or "worldPrivate" in filename:
                mp4_count = mp4_count + 1
        elif file_type == 'csv':
            #naming convention is just the date/timestamp, hard to name validate
            csv_count = csv_count + 1

    if mp4_count == 3 and csv_count == 1:
        return True
    else:
        return False

# This function validates that the files uploaded for data are correct, can do this from naming convention
def validate_data_files(file_list) -> bool:
    file_count = len(file_list)
    if file_count > 20 or file_count < 10:
        return False

    acceptable_files = ["eye0_timestamps.npy", "eye0.pldata", "eye1_timestamps.npy", "eye1.pldata",
                      "accel_timestamps.npy", "accel.pldata", "gyro_timestamps.npy", "gyro.pldata",
                      "odometry_timestamps.npy", "odometry.pldata", "world.intrinsics", "world.extrinsics",
                        "world_timestamps.npy", "marker_times.yaml", "world.pldata", "processedGaze", ".DS_Store", "gaze.npz"]

    for filename in file_list:
        if filename not in acceptable_files:
            print(filename)
            return False
    return True

atexit.register(delete_files_on_exit)

# Initial screen, with both files ready for upload
def main():
    global show_form1
    show_form1 = True
    global show_form2
    show_form2 = True
    reset_failures()
    new_files()

    return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

# Ran when upload video files button is clicked, checks and validates files that were uploaded
def upload_video():
    if request.method == 'POST':
        reset_failures()

        # Get the list of files from webpage
        files = request.files.getlist("file")
        # This checks for the case where no files are uploaded, and the upload files button is just clicked
        if len(files) == 1:
            set_failed_upload(1, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_video_upload=failed_video_upload, failed_data_upload=failed_data_upload)

        # Iterate for each file in the files List, and Save them
        for file in files:
            file.save(file.filename)
            global video_file_list
            video_file_list.append(file.filename)

        #File Validation
        if validate_video_files(video_file_list) is False:
            delete_files_in_list(video_file_list)
            video_file_list.clear()
            set_failed_upload(1, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_video_upload=failed_video_upload, failed_data_upload=failed_data_upload)

        #Runs if files are correctly uploaded and validated, naming convention for viewer (needs to be in static folder)
        # This code works when the application is run from run_me.py (outside of flaskr folder)
        # If that starting point is moved to init, need to modify this to take out "flaskr/" from the renames and appends
        for filename in video_file_list:
            if "worldPrivate" in filename:
                os.rename(filename, "flaskr/static/worldvideo.mp4")
            elif "eye0" in filename:
                os.rename(filename, "flaskr/static/eye0.mp4")
            elif "eye1" in filename:
                os.rename(filename, "flaskr/static/eye1.mp4")
            elif "csv" in filename:
                os.rename(filename, "flaskr/static/datatable.csv")

        video_file_list.clear()
        video_file_list.append("flaskr/static/worldvideo.mp4")
        video_file_list.append("flaskr/static/eye0.mp4")
        video_file_list.append("flaskr/static/eye1.mp4")
        video_file_list.append("flaskr/static/datatable.csv")

        print(video_file_list)

        set_showform(1, False)
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

# Ran when upload data files button is clicked, checks and validates files that were uploaded
def upload_data():
    if request.method == 'POST':
        reset_failures()

        # Get the list of files from webpage
        files = request.files.getlist("file")
        #This checks for the case where no files are uploaded, and the upload files button is just clicked
        if len(files) == 1:
            set_failed_upload(2, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_video_upload=failed_video_upload, failed_data_upload=failed_data_upload)

        # Iterate for each file in the files List, and Save them
        for file in files:
            file.save(file.filename)
            global data_file_list
            data_file_list.append(file.filename)

        # File Validation
        if validate_data_files(data_file_list) is False:
            delete_files_in_list(data_file_list)
            data_file_list.clear()
            set_failed_upload(2, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_video_upload=failed_video_upload, failed_data_upload=failed_data_upload)

        # Runs if files are correctly uploaded and validated
        set_showform(2, False)
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

# This function is ran when the upload video link form is submitted, attempts to download and validate the files found at that link
def upload_video_link():
    if request.method == 'POST':
        reset_failures()
        vid_link = request.form['video_link']

        if validate_link(vid_link, 0) is False:
            set_failed_link(1, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_data_link=failed_data_link, failed_video_link=failed_video_link)

        try:
            response = download_video_files(vid_link)
            extract_unzip(response)
        except:
            # Change this to form show/hide
            set_failed_link(1, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_data_link=failed_data_link, failed_video_link=failed_video_link)

        folders_list = []
        current_working_dir = os.getcwd()
        for folder in os.scandir(os.path.abspath(os.path.dirname(__file__))):
            if folder.is_dir():
                folders_list.append(folder)

        global video_folder_name
        for folder in folders_list:
            #Should pick out unzipped folder containing videos
            folder_name = folder.name
            if "-" in folder_name and "pycache" not in folder_name:
                video_folder_name = folder_name
                break

        video_dir = current_working_dir + '\\' + "flaskr" + '\\' + video_folder_name + '\\'
        files = os.listdir(video_dir)
        global video_file_list
        for file in files:
            video_file_list.append(file)
        if validate_video_files(video_file_list) is False:
            delete_files_in_list(video_file_list)
            set_failed_upload(1, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_data_link=failed_data_link, failed_video_link=failed_video_link)
        # Runs if files are correctly uploaded and validated
        set_showform(1, False)
        set_is_folder(1, True, video_folder_name)
        new_video_file_list = []
        for file in video_file_list:
            complete_file_path = "flaskr" + "\\" + video_folder_name + "\\" + file
            new_video_file_list.append(complete_file_path)
        video_file_list.clear()
        video_file_list = new_video_file_list

        # all of this code is to ensure files are found in the static folder, which is how the HTML runs them
        for filename in video_file_list:
            if "worldPrivate" in filename:
                os.rename(filename, "flaskr/static/worldvideo.mp4")
            elif "eye0" in filename:
                os.rename(filename, "flaskr/static/eye0.mp4")
            elif "eye1" in filename:
                os.rename(filename, "flaskr/static/eye1.mp4")
            elif "csv" in filename:
                os.rename(filename, "flaskr/static/datatable.csv")

        video_file_list.clear()
        video_file_list.append("flaskr/static/worldvideo.mp4")
        video_file_list.append("flaskr/static/eye0.mp4")
        video_file_list.append("flaskr/static/eye1.mp4")
        video_file_list.append("flaskr/static/datatable.csv")

        if get_showform(1) == False and get_showform(2) == False:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)
        else:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

# This function is ran when the upload data link form is submitted, attempts to download and validate the files found at that link
def upload_data_link():
    if request.method == 'POST':
        reset_failures()
        data_link = request.form['data_link']

        if validate_link(data_link, 1) is False:
            set_failed_link(2, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_data_link=failed_data_link, failed_video_link=failed_video_link)

        try:
            response = download_from_url(data_link)
            extract_unzip(response.content)
        except:
            #Change this to form show/hide
            set_failed_link(2, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_data_link=failed_data_link, failed_video_link=failed_video_link)

        folders_list = []
        current_working_dir = os.getcwd()
        for folder in os.scandir(os.path.abspath(os.path.dirname( __file__ ))):
            if folder.is_dir():
                folders_list.append(folder)

        global data_folder_name
        for folder in folders_list:
            folder_name = folder.name
            if "fixation" not in folder_name and "static" not in folder_name and "templates" not in folder_name and "__pycache__" not in folder_name:
                if "-" not in folder_name and "MAC" not in folder_name:
                    data_folder_name = folder_name
                    break


        data_dir = current_working_dir + '\\' + "flaskr" + '\\' + data_folder_name + '\\'
        files = os.listdir(data_dir)
        global data_file_list
        for file in files:
            data_file_list.append(file)

        if validate_data_files(data_file_list) is False:
            delete_files_in_list(data_file_list)
            set_failed_upload(2, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_data_link=failed_data_link, failed_video_link=failed_video_link)

        # Runs if files are correctly uploaded and validated
        set_showform(2, False)
        set_is_folder(2, True, data_folder_name)


        new_data_file_list = []
        for file in data_file_list:
            complete_file_path = "flaskr" + "\\" + data_folder_name + "\\" + file
            new_data_file_list.append(complete_file_path)
        data_file_list.clear()
        data_file_list = new_data_file_list

        if get_showform(1) == False and get_showform(2) == False:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)
        else:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

#The following two functions provide functionality for uploading different files after previous file upload, for both video and data
def upload_different_video():
    if request.method == 'POST':
        reset_failures()
        global video_file_list
        delete_files_in_list(video_file_list)
        video_file_list.clear()

        global show_form1
        show_form1 = True
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

def upload_different_data():
    if request.method == 'POST':
        reset_failures()
        global data_file_list
        delete_files_in_list(data_file_list)
        data_file_list.clear()
        delete_folders()

        global show_form2
        show_form2 = True
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

# This function renders the page that has helpful information on file upload conventions
def upload_help():
    reset_failures()
    return render_template("file-upload/file_upload_help.html")

# Return to main file upload from help, renders saved state
def back_to_file_upload():
    if request.method == 'POST':
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)


# The following two functions were provided to us by Brian Szekely, a UNR PhD student and a former student
# of Paul MacNeilage's Self Motion Lab.
# They work with the pldata files, turning them into readable format for our graphing code
def read_pldata(file_path):    
    try:
        with open(file_path, 'rb') as file:
            unpacker = msgpack.Unpacker(file, raw=False)
            data = []
            for packet in unpacker:
                data.append(packet)
    except OSError:
        print(f'File path: "{file_path}" not found.')
        print(f"Current working directory: {os.getcwd()}")
        raise OSError
    return data

def parse_pldata(data):
    unpacker = msgpack.Unpacker(BytesIO(data), raw=False)
    parsed_data = next(unpacker)

    # flatten nested structures
    flattened = {}
    for key, value in parsed_data.items():
        if isinstance(value, list):
            for i, item in enumerate(value):
                flattened[f"{key}_{i}"] = item
        else:
            flattened[key] = value

    return flattened

# This function was taken from Michelle, an individual who has worked on the VEDB and specifically published some
# information about accessing and visualizing the VEDB, in which this function was found.
# That can be found here: https://github.com/vedb/vedb-demos/blob/main/VEDB_demo_explore_session.ipynb
def load_as_dict(path):
    tmp = np.load(path, allow_pickle=True)
    params = {}
    for k, v in tmp.items():
        if isinstance(v, np.ndarray) and (v.dtype==np.dtype("O")):
            if v.shape==():
              params[k] = v.item()
            else:
              params[k] = v
    return params

# Some data files in the VEDB record NANs when the hardware stops recording (for whatever reason)
def count_nans(vel_list):
    nan_count = sum(1 for value in vel_list if isinstance(value, float) and math.isnan(value))
    print("Nan Count Ratio:", nan_count / len(vel_list))
    print("Nan Count:", nan_count)
    return nan_count

def generate_velocity_graphs(filename_list: list[str]):
    # assuming either 1. both files exist, 2. neither file exists
    global graph_file_list
    for filename in filename_list:
        data = read_pldata(filename)
        df = pd.DataFrame(data)
        linear_vel_0_list = []
        linear_vel_1_list = []
        linear_vel_2_list = []

        angular_velocity_0_list = []
        angular_velocity_1_list = []
        angular_velocity_2_list = []

        timestamp_list = []
        first_timestamp = parse_pldata(df[1].iloc[0])['timestamp']

        for i in range(len(df)):
            data_frame = parse_pldata(df[1].iloc[i])

            data_type_1 = 'linear_velocity_0'
            data_type_2 = 'linear_velocity_1'
            data_type_3 = 'linear_velocity_2'

            data_type_4 = 'angular_velocity_0'
            data_type_5 = 'angular_velocity_1'
            data_type_6 = 'angular_velocity_2'

            if not math.isnan(data_frame[data_type_1]):
                linear_vel_0_list.append(data_frame[data_type_1])
                linear_vel_1_list.append(data_frame[data_type_2])
                linear_vel_2_list.append(data_frame[data_type_3])

                angular_velocity_0_list.append(data_frame[data_type_4])
                angular_velocity_1_list.append(data_frame[data_type_5])
                angular_velocity_2_list.append(data_frame[data_type_6])

                timestamp_list.append(data_frame['timestamp'] - first_timestamp)

        #Plotly Plots: Dynamic interactable plots
        # fig = go.Figure()
        # fig.add_trace(go.Scatter(x=timestamp_list, y=linear_vel_0_list, name='Linear Velocity 0'))
        # fig.add_trace(go.Scatter(x=timestamp_list, y=linear_vel_1_list, name='Linear Velocity 1'))
        # fig.add_trace(go.Scatter(x=timestamp_list, y=linear_vel_2_list, name='Linear Velocity 2'))
        # fig.update_layout(title='Linear Velocity', xaxis_title='Time', yaxis_title='Linear Velocity',
        #                   legend_title='Lines')
        # fig.update_layout(width=500, height=257)
        #
        # lin_vel_json = dumps(fig, cls=utils.PlotlyJSONEncoder)
        #
        # fig = go.Figure()
        # fig.add_trace(go.Scatter(x=timestamp_list, y=angular_velocity_0_list, name='Angular Velocity 0'))
        # fig.add_trace(go.Scatter(x=timestamp_list, y=angular_velocity_1_list, name='Angular Velocity 1'))
        # fig.add_trace(go.Scatter(x=timestamp_list, y=angular_velocity_2_list, name='Angular Velocity 2'))
        # fig.update_layout(title='Angular Velocity', xaxis_title='Time', yaxis_title='Angular Velocity',
        #                   legend_title='Lines')
        # fig.update_layout(width=500, height=257)
        #
        # ang_vel_json = dumps(fig, cls=utils.PlotlyJSONEncoder)
        # json_list = [lin_vel_json, ang_vel_json]
        # return json_list

        json_timestamp = dumps(timestamp_list)

        json_lin0 = dumps(linear_vel_0_list)
        json_lin1 = dumps(linear_vel_1_list)
        json_lin2 = dumps(linear_vel_2_list)

        json_ang0 = dumps(angular_velocity_0_list)
        json_ang1 = dumps(angular_velocity_1_list)
        json_ang2 = dumps(angular_velocity_2_list)

        json_list = [json_timestamp, json_lin0, json_lin1, json_lin2, json_ang0, json_ang1, json_ang2]
        return json_list

def generate_gaze_graph(filename_list):
    for filename in filename_list:
        gaze_dict = load_as_dict(filename)
        left_gaze = gaze_dict['left']
        right_gaze = gaze_dict['right']

        left_timestamps = []
        right_timestamps = []
        left_norm_pos_x = []
        left_norm_pos_y = []
        right_norm_pos_x = []
        right_norm_pos_y = []

        left_first_timestamp = left_gaze['timestamp'][0]
        for value in left_gaze['timestamp']:
            left_timestamps.append(value - left_first_timestamp)
        for value in left_gaze['norm_pos']:
            left_norm_pos_x.append(value[0])
            left_norm_pos_y.append(value[1])

        right_first_timestamp = right_gaze['timestamp'][0]
        for value in  right_gaze['timestamp']:
            right_timestamps.append(value - right_first_timestamp)
        for value in  right_gaze['norm_pos']:
            right_norm_pos_x.append(value[0])
            right_norm_pos_y.append(value[1])

        # fig = go.Figure()
        # fig.add_trace(go.Scatter(x=left_timestamps, y=left_norm_pos_x, name='Left Norm Pos X'))
        # fig.add_trace(go.Scatter(x=left_timestamps, y=left_norm_pos_y, name='Left Norm Pos Y'))
        # fig.add_trace(go.Scatter(x=right_timestamps, y=right_norm_pos_x, name='Right Norm Pos X'))
        # fig.add_trace(go.Scatter(x=right_timestamps, y=right_norm_pos_y, name='Right Norm Pos Y'))
        # fig.update_layout(title='Normalized Gaze Position', xaxis_title='Time', yaxis_title='Norm Position',
        #                   legend_title='Lines')
        # fig.update_layout(width=500, height=257)
        #
        # gaze_json = dumps(fig, cls=utils.PlotlyJSONEncoder)

        json_left_timestamp = dumps(left_timestamps)
        json_left_norm_pos_x = dumps(left_norm_pos_x)
        json_left_norm_pos_y = dumps(left_norm_pos_y)

        json_right_timestamp = dumps(right_timestamps)
        json_right_norm_pos_x = dumps(right_norm_pos_x)
        json_right_norm_pos_y = dumps(right_norm_pos_y)

        gaze_json = [json_left_timestamp, json_left_norm_pos_x, json_left_norm_pos_y, json_right_timestamp, json_right_norm_pos_x, json_right_norm_pos_y]
        return gaze_json

# Loads the visualizer once files have been correctly uploaded
def load_visualizer():
    if request.method == 'POST':
        if not show_form1 and not show_form2:
            if get_is_folder(2):
                file_to_graph = "flaskr/" + get_folder_name(2) + "/odometry.pldata"
            else:
                file_to_graph = "odometry.pldata"
            # This returns a JSON_list, in the refactor this will go to the frontend JS for graph generation, in the form of lists not graphs
            vel_data = generate_velocity_graphs([file_to_graph])
            if get_is_folder(2):
                file_to_graph = "flaskr/" + get_folder_name(2) + "/gaze.npz"
            else:
                file_to_graph = "gaze.npz"
            gaze_data = generate_gaze_graph([file_to_graph])
            # ADD THIS BACK AS A VARIABLE WHEN YOU REFACTOR please :) [, gaze_JSON=graphs[2]]
            return render_template("visualizer/visualizer.html", velocity_timestamps = vel_data[0], linear_0 = vel_data[1],
                                   linear_1 = vel_data[2], linear_2 = vel_data[3], angular_0 = vel_data[4], angular_1 = vel_data[5], angular_2 = vel_data[6],
                                   left_gaze_timestamps = gaze_data[0], left_norm_pos_x = gaze_data[1], left_norm_pos_y = gaze_data[2],
                                   right_gaze_timestamps = gaze_data[3], right_norm_pos_x = gaze_data[4], right_norm_pos_y = gaze_data[5])
        else:
            raise Exception(f"Invalid Action") #how did it get here

#Function ran when the viewer's exit viewer button is clicked
def new_files():
    global video_file_list
    global data_file_list

    delete_files_in_list(video_file_list)
    delete_files_in_list(data_file_list)

    delete_folders()
    clear_lists()