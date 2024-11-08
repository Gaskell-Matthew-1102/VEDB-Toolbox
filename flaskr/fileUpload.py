import os
from dataclasses import field
from tkinter.filedialog import askdirectory

import threading

from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, SubmitField
from os import walk

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'csv', 'pldata', 'npy', 'yaml', 'intrinsics', 'extrinsics'}

app = Flask(__name__)
app.secret_key = 'paint THE sky'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class VideoForm(Form):
    vpath = StringField('Video Folder')
    submitV = SubmitField('Upload')

class DataForm(Form):
    dpath = StringField('Data Folder')
    submitD = SubmitField('Upload')

#Opens file explorer, allowing user to select the folder containing their video files
def get_video_path():
    video_path = '{}'.format(askdirectory(title='Choose a directory', initialdir=r'C:\ '))
    return video_path

#Opens file explorer, allowing user to select the folder containing their data files
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
    required_files = ["eye0_timestamps.npy", "eye0.pldata", "eye1_timestamps.npy", "eye1.pldata",
                      "accel_timestamps.npy", "accel.pldata", "gyro_timestamps.npy", "gyro.pldata"]
    file_list = list_files(dpath)
    for filename in file_list:
        if filename not in required_files:
            return False
    return True

#https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/FileUpload')
def main():
    return(render_template("file_upload.html"))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("here")
    if request.method == 'POST':
        if 'files[]' not in request.files:
            print("here2")
            return 'No file part'

        files = request.files.getlist('file')

        print("here2")
        for file in files:
            file.save(file.filename)
        print("not here")
        return "<h1>Files Uploaded Successfully.!</h1>"



@app.route('/FileUpload', methods=['GET', 'POST'])
def upload_video_folder():
    video_form = VideoForm()
    data_form = DataForm()

    videoflag = False
    dataflag = False

    if video_form.submitV.data and video_form.validate():
        videoflag = validate_video_path(video_form.submitV.data)


    if request.method == 'POST':

        vpath = request.form['video_directory']
        dpath = request.form['data_directory']

        videoflag = False
        dataflag = False

        if videoflag == False:
            videoflag = validate_video_path(vpath)
        elif dataflag == False:
            dataflag = validate_data_path(dpath)

        print(videoflag)
        print(dataflag)

    if videoflag == True and dataflag == False:
        return(render_template("main.html"))
    elif videoflag == False:
        return (render_template("main.html"))
    else:
        return (render_template("main.html"))

if __name__=='__main__':
    app.debug = True
    app.run()