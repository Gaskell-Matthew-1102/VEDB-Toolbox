from flask import *
import atexit
import os
import numpy as np
from pathlib import Path
import msgpack
import collections
import pandas as pd
from io import BytesIO
import zipfile
import requests

app = Flask(__name__)

video_file_list = []
data_file_list = []

show_form1 = True
show_form2 = True

failed_video_upload = False
failed_data_upload = False
failed_video_link = False
failed_data_link = False

are_videos_in_folder = False
is_data_in_folder = False

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

def set_is_folder(form_num: int, flag: bool) -> None:
    if form_num == 1:
        global are_videos_in_folder
        are_videos_in_folder = flag
    elif form_num == 2:
        global is_data_in_folder
        is_data_in_folder = flag

def get_is_folder(form_num: int) -> bool:
    if form_num == 1:
        return are_videos_in_folder
    elif form_num == 2:
        return is_data_in_folder

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

def get_folder_name(form_num: int) -> str:
    if form_num == 1:
        return video_folder_name
    elif form_num == 2:
        return data_folder_name

def delete_files_in_list(listed_files) -> None:
    for file in listed_files:
        if os.path.isfile(file):
            os.remove(file)

#Automatically deletes populated files on exit of python program
#could add a feature where users choose to keep these files(??)
def delete_files_on_exit() -> None:
    for file in video_file_list:
        if os.path.isfile(file):
            os.remove(file)
    for file in data_file_list:
        if os.path.isfile(file):
            os.remove(file)

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
def extract_unzip(link: str) -> bool:
    zip_url = link
    response = requests.get(zip_url)

    if response.status_code != 200:
        raise Exception(f"Failed to download file: {response.status_code}")

    zip_file = zipfile.ZipFile(BytesIO(response.content)) # get the zip file
    filepath = os.path.abspath(os.path.dirname( __file__ ))
    zip_file.extractall(filepath)
    return True

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

@app.route('/')
def main():
    global show_form1
    show_form1 = True
    global show_form2
    show_form2 = True
    reset_failures()

    return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_video', methods=['POST'])
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
        for filename in video_file_list:
            if "worldPrivate" in filename:
                os.rename(filename, "static/worldvideo.mp4")
            elif "eye0" in filename:
                os.rename(filename, "static/eye0.mp4")
            elif "eye1" in filename:
                os.rename(filename, "static/eye1.mp4")
            elif "csv" in filename:
                os.rename(filename, "static/datatable.csv")

        video_file_list.clear()
        video_file_list.append("static/worldvideo.mp4")
        video_file_list.append("static/eye0.mp4")
        video_file_list.append("static/eye1.mp4")
        video_file_list.append("static/datatable.csv")

        print(video_file_list)

        set_showform(1, False)
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_data', methods=['POST'])
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

@app.route('/upload_video_link', methods=['POST'])
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
            return "<h1>The download has failed.</h1>"

        folders_list = []
        current_working_dir = os.getcwd()
        for folder in os.scandir(os.path.abspath(os.path.dirname(__file__))):
            if folder.is_dir():
                folders_list.append(folder)

        global video_folder_name
        for folder in folders_list:
            #Should pick out unzipped folder containing videos
            if "-" in folder:
                video_folder_name = folder
                break

        video_dir = current_working_dir + video_folder_name
        global data_file_list
        for file in video_dir:
            video_file_list.append(file)

        if validate_data_files(video_file_list) is False:
            delete_files_in_list(video_file_list)
            #return something to report that link downloaded wrong files

        # Runs if files are correctly uploaded and validated
        set_showform(2, False)
        set_is_folder(2, True)

        for file in video_file_list:
            complete_file_path = video_folder_name + "/" + file
            video_file_list.append(complete_file_path)
            video_file_list.remove(file)

        if get_showform(1) == False and get_showform(2) == False:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)
        else:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_data_link', methods=['POST'])
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
            return "<h1>The download has failed.</h1>"

        folders_list = []
        current_working_dir = os.getcwd()
        for folder in os.scandir(os.path.abspath(os.path.dirname( __file__ ))):
            if folder.is_dir():
                folders_list.append(folder)

        global data_folder_name
        for folder in folders_list:
            if "-" not in folder and "MAC" not in folder:
                data_folder_name = folder
                break

        data_dir = current_working_dir + data_folder_name
        global data_file_list
        for file in data_dir:
            data_file_list.append(file)

        print(data_file_list)

        if validate_data_files(data_file_list) is False:
            delete_files_in_list(data_file_list)
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2,
                                   failed_data_link=failed_data_link, failed_video_link=failed_video_link)

        # Runs if files are correctly uploaded and validated
        set_showform(2, False)
        set_is_folder(2, True)

        for file in data_file_list:
            complete_file_path = data_folder_name + "/" + file
            data_file_list.append(complete_file_path)
            data_file_list.remove(file)

        if get_showform(1) == False and get_showform(2) == False:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)
        else:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

#The following two functions provide functionality for uploading different files after previous file upload, for both video and data
@app.route('/upload_different_video', methods=['POST'])
def upload_different_video():
    if request.method == 'POST':
        reset_failures()
        global video_file_list
        delete_files_in_list(video_file_list)

        global show_form1
        show_form1 = True
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_different_data', methods=['POST'])
def upload_different_data():
    if request.method == 'POST':
        reset_failures()
        global data_file_list
        delete_files_in_list(data_file_list)

        global show_form2
        show_form2 = True
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_help')
def upload_help():
    reset_failures()
    return render_template("file-upload/file_upload_help.html")

@app.route('/go_back', methods=['POST'])
def back_to_file_upload():
    if request.method == 'POST':
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/visualizer', methods=['POST'])
def load_visualizer():
    if request.method == 'POST':
        if not show_form1 and not show_form2:
            return render_template("visualizer/visualizer.html")
        else:
            raise Exception(f"Invalid Action") #how did it get here

if __name__ == '__main__':
    app.run(debug=True)