from flask import *
import atexit
import os
import numpy as np
from pathlib import Path
import msgpack
import collections
import pandas as pd


app = Flask(__name__)

file_list = []

def delete_files_on_exit():
    for file in file_list:
        if os.path.isfile(file):
            os.remove(file)

def validate_link(link, flag) -> bool:
    if "." not in link:
        return False
    if "osf.io" not in link and flag == 1:
        return False
    if "nyu.databrary.org" not in link and flag == 0:
        return False
    #Passes first check, still forced to hit others (exception)
    return True

def extract_unzip(file):
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

atexit.register(delete_files_on_exit)

@app.route('/')
def main():
    return render_template("test.html")

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':

        # Get the list of files from webpage
        files = request.files.getlist("file")

        # Iterate for each file in the files List, and Save them
        for file in files:
            file.save(file.filename)
            global file_list
            file_list.append(file.filename)
        return "<h1>Files Uploaded Successfully.!</h1>"

if __name__ == '__main__':
    app.run(debug=True)