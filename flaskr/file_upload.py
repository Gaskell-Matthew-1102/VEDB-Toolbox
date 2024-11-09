from flask import *
import atexit
import os
import numpy as np
from pathlib import Path
import msgpack
import collections
import pandas as pd

app = Flask(__name__)

video_file_list = []
data_file_list = []

show_form1 = True
show_form2 = True

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

#Two get functions for lists be utilized by the viewer application
def get_video_list() -> list:
    return video_file_list

def get_data_file_list() -> list:
    return data_file_list

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
def extract_unzip(file: str) -> int:
    test_link = validate_link
    if test_link is False:
        #raise Exception("Invalid link")
        return 2
    zip_url = file
    response = requests.get(zip_url)
    if response.status_code == 200:
        print("Download successful")
    else:
        #raise Exception(f"Failed to download file: {response.status_code}")
        #raise Exception("Download failed")
        return 3
    zip_file = zipfile.ZipFile(BytesIO(response.content))
    extracted_folder = getcwd()
    zip_file.extractall(extracted_folder)
    return 1

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
    if file_count > 15:
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

    return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if request.method == 'POST':

        # Get the list of files from webpage
        files = request.files.getlist("file")

        # Iterate for each file in the files List, and Save them
        for file in files:
            file.save(file.filename)
            global video_file_list
            video_file_list.append(file.filename)

        #File Validation
        if validate_video_files(video_file_list) is False:
            delete_files_in_list(video_file_list)
            video_file_list.clear()
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

        #Runs if files are correctly uploaded and validated
        set_showform(1, False)
        if get_showform(1) == False and get_showform(2) == False:
            return "<h1>Files Uploaded Successfully.!</h1>"
        else:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_data', methods=['POST'])
def upload_data():
    if request.method == 'POST':

        # Get the list of files from webpage
        files = request.files.getlist("file")

        # Iterate for each file in the files List, and Save them
        for file in files:
            file.save(file.filename)
            global data_file_list
            data_file_list.append(file.filename)

        # File Validation
        if validate_data_files(data_file_list) is False:
            delete_files_in_list(data_file_list)
            data_file_list.clear()
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

        # Runs if files are correctly uploaded and validated
        set_showform(2, False)
        if get_showform(1) == False and get_showform(2) == False:
            return "<h1>Files Uploaded Successfully.!</h1>"
        else:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_video_link', methods=['POST'])
def upload_video_link():
    if request.method == 'POST':
        vid_link = request.form['video_link']

        initial_files_list = os.listdir('.')

        if validate_link(vid_link, 0) is False:
            return "<h1>The provided link is invalid.</h1>"

        flag = extract_unzip(vid_link)
        if flag == 3:
            return "<h1>The download has failed.</h1>"

        global video_file_list
        video_file_list = os.listdir('.')

        for file in video_file_list:
            if file in initial_files_list:
                video_file_list.remove(file)

        if validate_data_files(video_file_list) is False:
            delete_files_in_list(video_file_list)
            #return something to report that link downloaded wrong files

        # Runs if files are correctly uploaded and validated
        set_showform(2, False)
        if get_showform(1) == False and get_showform(2) == False:
            return "<h1>Files Uploaded Successfully.!</h1>"
        else:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)


@app.route('/upload_data_link', methods=['POST'])
def upload_data_link():
    if request.method == 'POST':
        data_link = request.form['data_link']

        initial_files_list = os.listdir('.')
        if validate_link(data_link, 1) is False:
            return "<h1>The provided link is invalid.</h1>"

        flag = extract_unzip(data_link)

        if flag == 3:
            return "<h1>The download has failed.</h1>"

        global data_file_list
        data_file_list = os.listdir('.')

        for file in data_file_list:
            if file in initial_files_list:
                data_file_list.remove(file)

        if validate_data_files(data_file_list) is False:
            delete_files_in_list(data_file_list)
            #return something to report that link downloaded wrong files

        # Runs if files are correctly uploaded and validated
        set_showform(2, False)
        if get_showform(1) == False and get_showform(2) == False:
            return "<h1>Files Uploaded Successfully.!</h1>"
        else:
            return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

#The following two functions provide functionality for uploading different files after previous file upload, for both video and data
@app.route('/upload_different_video', methods=['POST'])
def upload_different_video():
    if request.method == 'POST':
        global video_file_list
        delete_files_in_list(video_file_list)

        global show_form1
        show_form1 = True
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_different_data', methods=['POST'])
def upload_different_data():
    if request.method == 'POST':
        global data_file_list
        delete_files_in_list(data_file_list)

        global show_form2
        show_form2 = True
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/upload_help')
def upload_help():
    return render_template("file-upload/file_upload_help.html")

@app.route('/go_back', methods=['POST'])
def back_to_file_upload():
    if request.method == 'POST':
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

@app.route('/visualizer', methods=['POST'])
def load_visualizer():
    if request.method == 'POST':
        if not show_form1 and not show_form2:
            return render_template("visualizer/main.html")
        else:
            raise Exception(f"Invalid Action")

if __name__ == '__main__':
    app.run(debug=True)