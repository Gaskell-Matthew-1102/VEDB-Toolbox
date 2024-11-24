import shutil

from flask import *
import atexit
import os
#import numpy as np
#from pathlib import Path
#import msgpack
#import collections
#import pandas as pd
from io import BytesIO
import zipfile
import requests

#Global variables
#File lists
video_file_list = []
data_file_list = []

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
    video_file_list.clear()
    data_file_list.clear()

def delete_folders():
    if get_is_folder(1):
        flask_folder = "flaskr" + "\\" + get_folder_name(1)
        if os.path.exists(flask_folder):
            shutil.rmtree(flask_folder)
    if get_is_folder(2):
        flask_folder = "flaskr" + "\\" + get_folder_name(2)
        if os.path.exists(flask_folder):
            shutil.rmtree(flask_folder)

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

# The original code for this function was given to us by Brian Szekely, a PhD student and former student of
# Dr. MacNeilage's Self-Motion Lab. It has been slightly altered to fit our code.
# This function takes in a link, downloads a zip file from that destination, and unzips it
def extract_unzip(link: str) -> bool:
    zip_url = link
    response = requests.get(zip_url)

    if response.status_code != 200:
        raise Exception(f"Failed to download file: {response.status_code}")

    zip_file = zipfile.ZipFile(BytesIO(response.content)) # get the zip file
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
    if file_count > 15 or file_count < 10:
        return False

    acceptable_files = ["eye0_timestamps.npy", "eye0.pldata", "eye1_timestamps.npy", "eye1.pldata",
                      "accel_timestamps.npy", "accel.pldata", "gyro_timestamps.npy", "gyro.pldata",
                      "odometry_timestamps.npy", "odometry.pldata", "world.intrinsics", "world.extrinsics",
                        "world_timestamps.npy", "marker_times.yaml", "world.pldata"]

    for filename in file_list:
        if filename not in acceptable_files:
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
            extract_unzip(vid_link)
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
            if "-" in folder and "pycache" not in folder:
                video_folder_name = folder_name
                break

        video_dir = current_working_dir + '\\' + "flaskr" + '\\' + video_folder_name + '\\'
        global video_file_list
        for file in video_dir:
            video_file_list.append(file)

        if validate_video_files(video_file_list) is False:
            delete_files_in_list(video_file_list)
            set_failed_upload(1, True)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_data_link=failed_data_link, failed_video_link=failed_video_link)

        # Runs if files are correctly uploaded and validated
        set_showform(2, False)
        set_is_folder(2, True, video_folder_name)

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
            extract_unzip(data_link)
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

# Loads the visualizer once files have been correctly uploaded
def load_visualizer():
    if request.method == 'POST':
        if not show_form1 and not show_form2:
            return render_template("visualizer/visualizer.html")
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