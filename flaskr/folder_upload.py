import os
from tkinter.filedialog import askdirectory # needs reconfiguring to flask

from flask import Flask, render_template, request, flash, redirect, url_for
from wtforms import Form, StringField, SubmitField

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'csv', 'pldata', 'npy', 'yaml', 'intrinsics', 'extrinsics'}

#This code was not used for our current method of handling files, but may be used next semester
#for a simpler way of utilizing locally downloaded files from a user's machine

#All of this code is our own, except for the last function which has been credited

#Opens file explorer, allowing user to select the folder containing their video files, RECONFIGURE
def get_video_path():
    video_path = '{}'.format(askdirectory(title='Choose a directory', initialdir=r'C:\ '))
    return video_path

#Opens file explorer, allowing user to select the folder containing their data files, RECONFIGURE
def get_data_path() -> str:
    data_path = '{}'.format(askdirectory(title='Choose a directory', initialdir=r'C:\ '))
    return data_path

#Function to count the number of files in a folder
def count_files(directory_path) -> int:
    count = 0
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if os.path.isfile(filepath):
            count = count + 1
    return count

#Function to count the number of folders within a folder
def count_folders(directory_path) -> int:
    count = 0
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if os.path.isdir(filepath):
            count = count + 1
    return count

#Function that returns a list of files within a folder
def list_files(directory_path):
    file_list = []
    for filename in os.listdir(directory_path):
        path = os.path.join(directory_path, filename)
        if os.path.isfile(path):
            file_list.append(filename)
    return file_list

#Function that returns the type of file
def get_file_type(directory_path) -> str:
    #change file_name to an _ if unused (made variable just incase)
    file_name, file_type = os.path.splitext(directory_path)
    return file_type

#Function to validate that the user's selected video folder is correct and valid
def validate_video_path(vpath) -> bool:
    file_count = count_files(vpath)
    # print("Number of files: ", file_count)
    if file_count != 4:
        return False
    file_list = list_files(vpath)
    mp4_count = 0
    csv_count = 0
    for filename in file_list:
        file_type = get_file_type(filename)
        if file_type == '.mp4':
            mp4_count = mp4_count + 1
        elif file_type == '.csv':
            csv_count = csv_count + 1
    if mp4_count == 3 and csv_count == 1:
        return True
    else:
        return False

#Function to validate that the user's selected data folder is correct and valid
def validate_data_path(dpath) -> bool:
    file_count = count_files(dpath)
    folder_count = count_folders(dpath)
    if folder_count > 1 and 20 >= file_count <= 10:
        return False
    acceptable_files = ["eye0_timestamps.npy", "eye0.pldata", "eye1_timestamps.npy", "eye1.pldata",
                        "accel_timestamps.npy", "accel.pldata", "gyro_timestamps.npy", "gyro.pldata",
                        "odometry_timestamps.npy", "odometry.pldata", "world.intrinsics", "world.extrinsics",
                        "world_timestamps.npy", "marker_times.yaml", "world.pldata"]
    file_list = list_files(dpath)
    for filename in file_list:
        if filename not in acceptable_files:
            return False
    return True

# This function was sourced from: https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
