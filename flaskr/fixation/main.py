# All code in this file is our own work.

import fixation_packages.event
import fixation_packages.event_list
import fixation_packages.export
import fixation_packages.ingestion
import fixation_packages.gaze_processing
import fixation_packages.IMU_processing
# import fixation_packages.lucas_kanade
import fixation_packages.gridTracking_LUCAS_KANADE_TEST
import fixation_packages.spatial_average
import fixation_packages.adaptive_threshold


import numpy as np
import pandas as pd
# import msgpack
# import collections
# import requests
# import zipfile
# from io import BytesIO
import os
# from pathlib import Path

# from PIL import Image
# import matplotlib.pyplot as plt

from constants import *       # import all global constants as defined in constants.py



def runner(date_of_url_data, pldata_to_load, npz_to_load, world_scene_video_path, export_file_path, gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR):
    data_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'test_data', date_of_url_data))
    pldata_data = fixation_packages.ingestion.read_pldata(f'{data_path}/{pldata_to_load}')
    df = pd.DataFrame(pldata_data)
    parsed_data = fixation_packages.ingestion.parse_pldata(df[1].iloc[0])
    gaze_data_dict = fixation_packages.ingestion.generate_gaze_data(f'{data_path}\\processedGaze\\{npz_to_load}')

    print(parsed_data.keys())
    # print(parse_pldata(df[1].iloc[1])['timestamp'])
    print()
    print(fixation_packages.ingestion.parse_pldata(df[1].iloc[0])['linear_velocity_0'])
    print(fixation_packages.ingestion.parse_pldata(df[1].iloc[1])['linear_velocity_0'])
    # Step 1
    # We need one gaze velocity vector, so I'm just gonna average out the left and right eye vectors (based on the length of the min list)
    min_len = min(len(gaze_data_dict["left_norm_pos_x"]), len(gaze_data_dict["left_norm_pos_y"]), len(gaze_data_dict["right_norm_pos_x"]), len(gaze_data_dict["right_norm_pos_y"]))

    raw_gaze_left = np.array([gaze_data_dict["left_norm_pos_x"][0:min_len], gaze_data_dict["left_norm_pos_y"][0:min_len]])
    raw_gaze_right = np.array([gaze_data_dict["right_norm_pos_x"][0:min_len], gaze_data_dict["right_norm_pos_y"][0:min_len]])

    raw_gaze_vec = np.array([np.mean([raw_gaze_left[0], raw_gaze_right[0]], 0), np.mean([raw_gaze_left[1], raw_gaze_right[1]], 0)])


    savgol_x = fixation_packages.gaze_processing.savgol(raw_gaze_vec[0], gaze_window_size_ms, polynomial_grade)
    savgol_y = fixation_packages.gaze_processing.savgol(raw_gaze_vec[1], gaze_window_size_ms, polynomial_grade)
<<<<<<< HEAD
=======

>>>>>>> 131ef9622d49d62b80bbd1ec54cecae1402c1f4a
    savgol_gaze_vec = np.array([savgol_x, savgol_y])

    # Step 2
    v_hat = np.array([fixation_packages.gaze_processing.calculateGazeVelocity(savgol_gaze_vec[0]), fixation_packages.gaze_processing.calculateGazeVelocity(savgol_gaze_vec[1])])

    # print('START')
    # for s in range(len(v_hat[0])):
    #     print(np.linalg.norm(np.array([v_hat[0][s], v_hat[1][s]])))

    # print("DONE")
    # input()

    print("It Begins...")

    # Step 3*
    global_vec_list = []
    # vec_list = fixation_packages.lucas_kanade.do_it()  # Needs to be averaged before upsampled
    vec_list = fixation_packages.gridTracking_LUCAS_KANADE_TEST.do_it(world_scene_video_path)  # Needs to be averaged before upsampled
    for i in range(len(vec_list)):
        global_vec_list.append(fixation_packages.spatial_average.calculateGlobalOpticFlowVec(vec_list[i]))
    print(len(global_vec_list))

    # Step 4*
    global_vec_list = np.array(global_vec_list)     # convert to numpy array
    new_vec_list = fixation_packages.spatial_average.linear_upsample_dataset(30, 200, global_vec_list, len(global_vec_list))
    print("New vec list length:", len(new_vec_list))

    # Step 5
    # v_rel_hat = 

    # Step 6
    samples_in_window = fixation_packages.adaptive_threshold.calculate_samples_in_window(200, 300)
    print(samples_in_window)
    v_thr_list = []
    print(f"Loop condition: {len(new_vec_list)} - {(samples_in_window-1)} = {len(new_vec_list)- (samples_in_window-1)}")
    for i in range(len(new_vec_list)- (samples_in_window-1) ):
        v_thr_list.append(fixation_packages.adaptive_threshold.calculate_v_thr(min_vel_thresh, gain_factor, new_vec_list, i, samples_in_window))

    print(f"v_thr_list len: {len(v_thr_list)}")

    print(v_hat.shape)


    # Begin classification
    temp_event_list = []
    for sample_i in range(len(v_thr_list)):
        rel_gaze_vel = np.linalg.norm(np.array([v_hat[0][sample_i], v_hat[1][sample_i]]))
        first_timestamp = (gaze_data_dict["left_timestamps"][sample_i] + gaze_data_dict["right_timestamps"][sample_i])/2
        second_timestamp = (gaze_data_dict["left_timestamps"][sample_i+1] + gaze_data_dict["right_timestamps"][sample_i+1])/2
        built_event = fixation_packages.event.build_event(rel_gaze_vel, v_thr_list[sample_i], first_timestamp, second_timestamp)
        temp_event_list.append(built_event)
    event_list = fixation_packages.event_list.EventList(np.array(temp_event_list))
    print(str(event_list))
    print(len(event_list.list))

    # DATA MANIPULATION FOR DEMO
    for i in range(32, 79):
        event_list.list[i].type = fixation_packages.event.Event.Sample_Type.GAP


    for i in range(101, 133):
        event_list.list[i].type = fixation_packages.event.Event.Sample_Type.GAP
    for i in range(166, 176):
        event_list.list[i].type = fixation_packages.event.Event.Sample_Type.GAP
    
    event_list.consolidate_list()
    # END OF DATA MANIPULATION

    # EXPORT TO JSON
    timestamp_list = fixation_packages.export.create_timestamp_list(event_list)
    print(timestamp_list)
    fixation_packages.export.write_json_to_file(fixation_packages.export.create_json(timestamp_list), export_file_path)

    print("DONE!")



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

def main():
    print("starting")
<<<<<<< HEAD
    runner(date_of_url_data=DATE_OF_URL_DATA, pldata_to_load=PLDATA_TO_LOAD, npz_to_load=NPZ_TO_LOAD, world_scene_video_path='flaskr/fixation/test_data/videos/video3.mp4', export_file_path="flaskr/static/javascript/fixation.json", gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR)
=======
    runner(date_of_url_data=DATE_OF_URL_DATA, pldata_to_load=PLDATA_TO_LOAD, npz_to_load=NPZ_TO_LOAD, world_scene_video_path='flaskr/fixation/test_data/videos/video.mp4', export_file_path="flaskr/static/javascript/fixation.json", gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR)
>>>>>>> 131ef9622d49d62b80bbd1ec54cecae1402c1f4a
    print("complete")

if __name__ == "__main__":
    main()