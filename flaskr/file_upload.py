# All of the code in this file is our own, apart from some pldata functions, which have been credited below

import shutil
from multiprocessing import Process, Manager

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
from multiprocessing import Process
from flaskr.fixation.main import runner as fixation_main

import plotly.graph_objects as go
from plotly import utils
from json import dumps







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
        # for value in left_gaze['timestamp']:
        #     left_timestamps.append(value - left_first_timestamp)
        counter = 0
        for value in left_gaze['norm_pos']:
            if value[0] < 1.0 and value[0] > -0.1 and value[1] < 1.0 and value[1] > -0.1:
                left_norm_pos_x.append(value[0])
                left_norm_pos_y.append(value[1])
                left_timestamps.append(left_gaze['timestamp'][counter] - left_first_timestamp)
                counter = counter + 1

        right_first_timestamp = right_gaze['timestamp'][0]
        # for value in  right_gaze['timestamp']:
        #     right_timestamps.append(value - right_first_timestamp)
        counter = 0
        for value in  right_gaze['norm_pos']:
            if value[0] < 1.0 and value[0] > -0.1 and value[1] < 1.0 and value[1] > -0.1:
                right_norm_pos_x.append(value[0])
                right_norm_pos_y.append(value[1])
                right_timestamps.append(right_gaze['timestamp'][counter] - right_first_timestamp)
                counter = counter + 1

        # NON DOWN SAMPLED TIMESTAMPS (around 82000 left or 78000 right), removed <0 and >1, i think those are out of bounds
        # json_left_timestamp = dumps(left_timestamps)
        # json_left_norm_pos_x = dumps(left_norm_pos_x)
        # json_left_norm_pos_y = dumps(left_norm_pos_y)
        #
        # json_right_timestamp = dumps(right_timestamps)
        # json_right_norm_pos_x = dumps(right_norm_pos_x)
        # json_right_norm_pos_y = dumps(right_norm_pos_y)

        # DOWN SAMPLED TIMESTAMPS, these have 1/10 of the original value so around 8200 left or 7800 right
        sampled_left_x = left_norm_pos_x[::10]
        sampled_left_y = left_norm_pos_y[::10]
        sampled_right_x = right_norm_pos_x[::10]
        sampled_right_y = right_norm_pos_y[::10]

        sampled_left_time = left_timestamps[::10]
        sampled_right_time = right_timestamps[::10]

        json_left_timestamp = dumps(sampled_left_time)
        json_left_norm_pos_x = dumps(sampled_left_x)
        json_left_norm_pos_y = dumps(sampled_left_y)

        json_right_timestamp = dumps(sampled_right_time)
        json_right_norm_pos_x = dumps(sampled_right_x)
        json_right_norm_pos_y = dumps(sampled_right_y)

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

            # Start fixation algorithm here!
            """
            Data file list: ['accel.pldata', 'accel_timestamps.npy', 'eye0.pldata', 'eye0_timestamps.npy', 'eye1.pldata', 'eye1_timestamps.npy', 'gyro.pldata', 'gyro_timestamps.npy', 'marker_times.yaml', 'odometry.pldata', 'odometry_timestamps.npy', 'world.extrinsics', 'world.intrinsics', 'world.pldata', 'world_timestamps.npy']
            Graph files: []
            Video files: ['flaskr/static/worldvideo.mp4', 'flaskr/static/eye0.mp4', 'flaskr/static/eye1.mp4', 'flaskr/static/datatable.csv']
            """

            data_files = get_data_file_list()
            video_files = get_video_list()

            print(data_files)
            print(video_files)


            if odometry_file == "":
                odometry_file = "NO IMU DATA"

            global SESSION_NAME
            global EXPORT_JSON_PATH
            global EXPORT_PARAMETER_PATH
            SESSION_NAME = "fixation"
            

            # EXPORT_JSON_PATH = "flaskr/fixation/export/export_fixation.json"
            EXPORT_JSON_PATH = f"{EXPORT_FOLDER_PATH}/{SESSION_NAME}.json"
            # EXPORT_PARAMETERS_PATH = "flaskr/fixation/export/export_parameters.txt"
            EXPORT_PARAMETER_PATH = f"{EXPORT_FOLDER_PATH}/{SESSION_NAME}_parameters.txt"

            

            start_fixation_algorithm(fix_det_args)

            # This returns a JSON_list, in the refactor this will go to the frontend JS for graph generation, in the form of lists not graphs
            vel_data = generate_velocity_graphs([file_to_graph])
            if get_is_folder(2):
                file_to_graph = "flaskr/" + get_folder_name(2) + "/gaze.npz"
            else:
                file_to_graph = "gaze.npz"
            gaze_data = generate_gaze_graph([file_to_graph])

            return render_template("visualizer/visualizer.html", velocity_timestamps = vel_data[0], linear_0 = vel_data[1],
                                   linear_1 = vel_data[2], linear_2 = vel_data[3], angular_0 = vel_data[4], angular_1 = vel_data[5], angular_2 = vel_data[6],
                                   left_gaze_timestamps = gaze_data[0], left_norm_pos_x = gaze_data[1], left_norm_pos_y = gaze_data[2],
                                   right_gaze_timestamps = gaze_data[3], right_norm_pos_x = gaze_data[4], right_norm_pos_y = gaze_data[5])
        else:
            raise Exception(f"Invalid Action") #how did it get here



def check_fixation_status():
    # Check if the JSON file generated by fixation algo exists
    file_exists = os.path.exists(EXPORT_JSON_PATH)
    if file_exists:
        if EXPORT_JSON_PATH not in data_file_list:
            data_file_list.append(EXPORT_JSON_PATH)
        if EXPORT_PARAMETER_PATH not in data_file_list:
            data_file_list.append(EXPORT_PARAMETER_PATH)

    return jsonify(file=EXPORT_JSON_PATH.split("/", 1)[1] if file_exists else "")

def download_graphs():
    linear_graph = request.args.get('linearGraph')
    angular_graph = request.args.get('angularGraph')
    gaze_graph = request.args.get('gazeGraph')

    linear_file_name = request.args.get('linearFileName')
    angular_file_name = request.args.get('angularFileName')
    gaze_file_name = request.args.get('gazeFileName')

    if not os.path.exists("graphs"):
        os.mkdir("graphs")

    linear_graph.write_image("images" + linear_file_name + ".png")
    angular_graph.write_image("images" + angular_file_name + ".png")
    gaze_graph.write_image("images" + gaze_file_name + ".png")

#Function ran when the viewer's exit viewer button is clicked
def new_files():
    delete_files_in_list(video_file_list)
    delete_files_in_list(data_file_list)

    delete_folders()
    clear_lists()
