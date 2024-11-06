from operator import truediv

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

def delete_files_in_list(listed_files) -> None:
    for file in listed_files:
        if os.path.isfile(file):
            os.remove(file)

def delete_files_on_exit():
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

def extract_unzip(file: str) -> None:
    test_link = validate_link
    if test_link is False:
        raise Exception("Invalid link")
    zip_url = file
    response = requests.get(zip_url)
    if response.status_code == 200:
        print("Download successful")
    else:
        raise Exception(f"Failed to download file: {response.status_code}")
    zip_file = zipfile.ZipFile(BytesIO(response.content))
    extracted_folder = getcwd()
    zip_file.extractall(extracted_folder)

def validate_video_files(file_list) -> bool:
    file_count = len(file_list)

    if file_count != 4:
        return False

    mp4_count = 0
    csv_count = 0

    for filename in file_list:
        file_type = filename.split(".", 1)[1]
        if file_type == 'mp4':
            mp4_count = mp4_count + 1
        elif file_type == 'csv':
            csv_count = csv_count + 1

    if mp4_count == 3 and csv_count == 1:
        return True
    else:
        return False

def validate_data_files(file_list) -> bool:
    file_count = len(file_list)
    if file_count != 10:
        return False

    required_files = ["eye0_timestamps.npy", "eye0.pldata", "eye1_timestamps.npy", "eye1.pldata",
                      "accel_timestamps.npy", "accel.pldata", "gyro_timestamps.npy", "gyro.pldata",
                      "odometry_timestamps.npy", "odometry.pldata"]

    for filename in file_list:
        if filename not in required_files:
            return False
    return True

atexit.register(delete_files_on_exit)

@app.route('/')
def main():
    return render_template("file-upload/test.html", show_form1=show_form1, show_form2=show_form2)

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
            return render_template("file-upload/test.html", show_form1=show_form1, show_form2=show_form2)

        #Runs if files are correctly uploaded and validated
        set_showform(1, False)
        if get_showform(1) == False and get_showform(2) == False:
            return "<h1>Files Uploaded Successfully.!</h1>"
        else:
            return render_template("file-upload/test.html", show_form1=show_form1, show_form2=show_form2)

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
            return render_template("file-upload/test.html", show_form1=show_form1, show_form2=show_form2)

        # Runs if files are correctly uploaded and validated
        set_showform(2, False)
        if get_showform(1) == False and get_showform(2) == False:
            return "<h1>Files Uploaded Successfully.!</h1>"
        else:
            return render_template("file-upload/test.html", show_form1=show_form1, show_form2=show_form2)

if __name__ == '__main__':
    app.run(debug=True)