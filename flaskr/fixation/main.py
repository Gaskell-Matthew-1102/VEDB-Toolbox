# All code in this file is our own work.

import fixation_packages.event
from fixation_packages.ingestion import extract_unzip, read_pldata, parse_pldata, generate_gaze_data
from fixation_packages.gaze_processing import savgol, calculateGazeVelocity
from fixation_packages.IMU_processing import calculate_optic_flow_vec, quat_to_euler
from fixation_packages.lucas_kanade import do_it
import fixation_packages.spatial_average
from fixation_packages.adaptive_threshold import calculate_v_thr, calculate_samples_in_window


import numpy as np
import pandas as pd
import msgpack
import collections
import requests
import zipfile
from io import BytesIO
import os
from pathlib import Path

from PIL import Image
import matplotlib.pyplot as plt

from constants import *       # import all global constants as defined in constants.py


def main():
    data_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'test_data', DATE_OF_URL_DATA))
    pldata_data = read_pldata(f'{data_path}/{PLDATA_TO_LOAD}')
    df = pd.DataFrame(pldata_data)
    parsed_data = parse_pldata(df[1].iloc[0])
    gaze_data_dict = generate_gaze_data(f'{data_path}\\processedGaze\\{NPZ_TO_LOAD}')

    print(parsed_data.keys())
    # print(parse_pldata(df[1].iloc[1])['timestamp'])
    dt = parse_pldata(df[1].iloc[1])['timestamp'] - parse_pldata(df[1].iloc[0])['timestamp']
    dpos = parse_pldata(df[1].iloc[1])['position_0'] - parse_pldata(df[1].iloc[0])['position_0']
    print()
    print(parse_pldata(df[1].iloc[0])['linear_velocity_0'])
    print(parse_pldata(df[1].iloc[1])['linear_velocity_0'])
    # Step 1
    # We need one gaze velocity vector, so I'm just gonna average out the left and right eye vectors (based on the length of the min list)
    min_len = min(len(gaze_data_dict["left_norm_pos_x"]), len(gaze_data_dict["left_norm_pos_y"]), len(gaze_data_dict["right_norm_pos_x"]), len(gaze_data_dict["right_norm_pos_y"]))

    raw_gaze_left = np.array([gaze_data_dict["left_norm_pos_x"][0:min_len], gaze_data_dict["left_norm_pos_y"][0:min_len]])
    raw_gaze_right = np.array([gaze_data_dict["right_norm_pos_x"][0:min_len], gaze_data_dict["right_norm_pos_y"][0:min_len]])

    raw_gaze_vec = np.array([np.mean([raw_gaze_left[0], raw_gaze_right[0]], 0), np.mean([raw_gaze_left[1], raw_gaze_right[1]], 0)])


    savgol_x = savgol(raw_gaze_vec[0], window_length=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE)
    savgol_y = savgol(raw_gaze_vec[1], window_length=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE)

    savgol_gaze_vec = np.array([savgol_x, savgol_y])

    # Step 2
    v_hat = np.array([calculateGazeVelocity(savgol_gaze_vec[0]), calculateGazeVelocity(savgol_gaze_vec[1])])

    # print(pd.to_datetime(parse_pldata(df[1].iloc[1])['source_timestamp'], unit='s'))

    # "2023_06_01_18_47_34" timestamp starts at 332.054984618, source timestamp starts at 1685659655.7981853
    # "2020_10_10_15_06_26" timestamp starts at 85.177573867, source timestamp starts at 1602367593.3724933



    # for i in range(len(list_all)-1):
    #     calculate_optic_flow_vec(list_all[i], list_all[i+1])

    # W_QUAT = parsed_data['orientation_0']
    # X_QUAT = parsed_data['orientation_1']
    # Y_QUAT = parsed_data['orientation_2']
    # Z_QUAT = parsed_data['orientation_3']

    # quaternion_vec = np.column_stack((W_QUAT, X_QUAT, Y_QUAT, Z_QUAT))
    # print()
    # print(quat_to_euler(quaternion_vec))

    # calculate_optic_flow_vec(parse_pldata(df[1].iloc[1]), parse_pldata(df[1].iloc[2]))

    print("It Begins...")

    global_vec_list = []
    vec_list = do_it()  # Needs to be averaged before upsampled
    for i in range(len(vec_list)):
        global_vec_list.append(fixation_packages.spatial_average.calculateGlobalOpticFlowVec(vec_list[i]))
    print(len(global_vec_list))


    new_vec_list = fixation_packages.spatial_average.linear_upsample_dataset(30, 200, global_vec_list, len(global_vec_list))
    print("New vec list length:", len(new_vec_list))


    samples_in_window = calculate_samples_in_window(200, 300)
    print(samples_in_window)

    v_thr_list = []
    for i in range(len(new_vec_list)- (samples_in_window-1) ):
        v_thr_list.append(calculate_v_thr(MIN_VEL_THRESH, GAIN_FACTOR, new_vec_list, i, samples_in_window))

    print(len(v_thr_list))
    print("DONE!")

    # Begin classification
    # for sample in range(len(v_thr_list)):
    #     if fixation_packages.event.classify_event()





    # OUTPUT OF print(parsed_data):
    # {'topic': 'odometry', 
    # 'timestamp': 332.054984618, 
    # 'source_timestamp': 1685659655.7981853, 
    # 'tracker_confidence': 2, 
    # 'position_0': 0.0, 
    # 'position_1': 0.0, 
    # 'position_2': 0.0, 
    # 'orientation_0': 0.9354915618896484, 
    # 'orientation_1': -0.31645840406417847, 
    # 'orientation_2': -0.03516574949026108, 
    # 'orientation_3': -0.15320907533168793, 
    # 'linear_velocity_0': 0.0, 
    # 'linear_velocity_1': 0.0, 
    # 'linear_velocity_2': 0.0, 
    # 'angular_velocity_0': 0.5675381422042847, 
    # 'angular_velocity_1': -0.6258752942085266, 
    # 'angular_velocity_2': 0.18717604875564575, 
    # 'linear_acceleration_0': 0.0, 
    # 'linear_acceleration_1': 0.0, 
    # 'linear_acceleration_2': 0.0, 
    # 'angular_acceleration_0': 6.18303108215332, 
    # 'angular_acceleration_1': 6.18303108215332, 
    # 'angular_acceleration_2': -4.951601982116699}

main()