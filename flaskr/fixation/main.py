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

X_RES = 192
Y_RES = 192


def runner(date_of_url_data, pldata_to_load, npz_to_load, world_scene_video_path, export_file_path, gaze_window_size_ms, polynomial_grade, min_vel_thresh, gain_factor, initial_world_hz, desired_world_hz):
    data_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'test_data', date_of_url_data))
    # pldata_data = fixation_packages.ingestion.read_pldata(f'{data_path}/{pldata_to_load}')
    # df = pd.DataFrame(pldata_data)
    # parsed_data = fixation_packages.ingestion.parse_pldata(df[1].iloc[0])
    gaze_data_dict = fixation_packages.ingestion.generate_gaze_data(f'{data_path}\\processedGaze\\{npz_to_load}')

    # print(parsed_data.keys())
    # print(parse_pldata(df[1].iloc[1])['timestamp'])
    # print()
    # print(fixation_packages.ingestion.parse_pldata(df[1].iloc[0])['linear_velocity_0'])
    # print(fixation_packages.ingestion.parse_pldata(df[1].iloc[1])['linear_velocity_0'])
    # Step 1
    # We need one gaze velocity vector, so I'm just gonna average out the left and right eye vectors (based on the length of the min list)
    min_len = min(len(gaze_data_dict["left_norm_pos_x"]), len(gaze_data_dict["left_norm_pos_y"]), len(gaze_data_dict["right_norm_pos_x"]), len(gaze_data_dict["right_norm_pos_y"]))

    # Generate gaze timestamp list to calculate velocity
    # print(gaze_data_dict.keys())
    gaze_timestamp = fixation_packages.gaze_processing.get_timestamp_list(gaze_data_dict, min_len)
    # for i in range(10000):
    #     print(gaze_timestamp[i+1] - gaze_timestamp[i])
    # input()

    raw_gaze_vec_ = fixation_packages.gaze_processing.calculate_raw_gaze_vector(gaze_data_dict, x_res=X_RES, y_res=Y_RES)
    

    savgol_x = fixation_packages.gaze_processing.savgol(raw_gaze_vec_[0], gaze_window_size_ms, polynomial_grade)
    savgol_y = fixation_packages.gaze_processing.savgol(raw_gaze_vec_[1], gaze_window_size_ms, polynomial_grade)
    savgol_gaze_vec = np.array(np.column_stack([savgol_x, savgol_y]))
    # print(savgol_gaze_vec.shape)
    # input()
    # mint = 0.0
    # maxt = 0.0
# THE GAZE VECTOR IS NORMALISED, MUST CONVERT TO PIXEL SPACE
    # for i in range(len(savgol_gaze_vec)):
    #     mint = min(np.linalg.norm(np.array([savgol_gaze_vec[i][0], savgol_gaze_vec[i][1]])), mint)
    #     maxt = max(np.linalg.norm(np.array([savgol_gaze_vec[i][0], savgol_gaze_vec[i][1]])), maxt)
    # print("min: ", mint)
    # print("max: ", maxt)
    # input()
    # count = 0
    # other = 0
    # for i in range(0, len(savgol_gaze_vec), 1):
    #     s = np.linalg.norm(np.array([savgol_gaze_vec[i][0], savgol_gaze_vec[i][1]]))
    #     if s <= temp_avg:
    #         # print(f"Savgol gaze vector magnitudes ({i}): {s}")
    #         count += 1
    #     else:
    #         other += 1
    # print('done: ', count, other)
    # input()

    # Step 2
    # print(f"savgolgaze_vec_shape: {savgol_gaze_vec.shape}")
    # print(savgol_gaze_vec[:])
    # print(savgol_gaze_vec[:][0])
    # print(savgol_gaze_vec[:][1])
    # input()

    v_hat = fixation_packages.gaze_processing.calculateGazeVelocity(savgol_gaze_vec, gaze_timestamp)
    # print(v_hat.shape)
    # input()

    print("It Begins...")

    # Step 3*
    global_OF_vec_list = []
    # vec_list = fixation_packages.lucas_kanade.do_it()  # Needs to be averaged before upsampled
    # global_OF_vec_list = fixation_packages.gridTracking_LUCAS_KANADE_TEST.do_it(world_scene_video_path)  # Needs to be averaged before upsampled



    ############## SAVE THE OUTPUT OF LUCAS-KANADE TO SAVE TIME #################
    import pickle
    # with open('flaskr/fixation/saved_lucas_kanade_data_entire_dataset', 'wb') as fp:
    #     pickle.dump(vec_list, fp)

    # input("AAA")

    with open ('flaskr/fixation/saved_lucas_kanade_data_111s', 'rb') as fp:
        global_OF_vec_list = pickle.load(fp)


    # for i in range(len(vec_list)):
    #     global_OF_vec_list.append(fixation_packages.spatial_average.calculateGlobalOpticFlowVec(vec_list[i]))
    global_OF_vec_list = np.array(global_OF_vec_list)     # convert to numpy array
    [print(global_OF_vec_list[x]) for x in range(10)]
    # input('guh')

    # for i in range(len(global_OF_vec_list)):
    #     print(f"Global OF magnitudes ({i+1}): {np.linalg.norm(np.array([global_OF_vec_list[i][0], global_OF_vec_list[i][1]]))}")
    # input()

    # Step 4*
    new_vec_list = fixation_packages.spatial_average.linear_upsample_dataset(initial_world_hz, desired_world_hz, global_OF_vec_list)
    print("New vec list length:", len(new_vec_list))

    # Step 5
    print(f"v hat shape: {v_hat.shape}")
    print(f"Global vec list shape: {global_OF_vec_list.shape}")
    v_rel, status_code = fixation_packages.adaptive_threshold.gaze_velocity_correction(v_hat, global_OF_vec_list)

    # Step 6
    samples_in_window = fixation_packages.adaptive_threshold.calculate_samples_in_window(200, 300)
    v_thr_list = []
    for i in range(len(new_vec_list)- (samples_in_window-1) ):
        v_thr_list.append(fixation_packages.adaptive_threshold.calculate_v_thr(min_vel_thresh, gain_factor, new_vec_list, i, samples_in_window))

    # print(f"v_thr_list len: {len(v_thr_list)}")
    # print(v_thr_list)



    # Begin classification
    temp_event_list = []
    for sample_i in range(min(len(v_rel), len(v_thr_list))):
        rel_gaze_vel = np.linalg.norm(np.array([v_rel[sample_i][0], v_rel[sample_i][1]]))

        first_timestamp = gaze_timestamp[sample_i]
        second_timestamp = gaze_timestamp[sample_i+1]

        start_pos = savgol_gaze_vec[sample_i]
        end_pos = savgol_gaze_vec[sample_i+1]

        built_event = fixation_packages.event.build_event(rel_gaze_vel, v_thr_list[sample_i], first_timestamp, second_timestamp, start_pos, end_pos)
        temp_event_list.append(built_event)
    event_list = fixation_packages.event_list.EventList(np.array(temp_event_list))

    # 
    # 
    # 
    # 
    # 
    #       Can possibly integrate the velocity over the time of the sample to see the displacement over that sample? used to get positions of the eyes
    # 
    # 
    # 
    #

    # input()
    # print(str(event_list))
    # print(len(event_list.list))
    print("Summary 1:",event_list.return_list_summary())
    event_list.consolidate_list()
    print("Summary 2:",event_list.return_list_summary())
    event_list.apply_filter(fixation_packages.event.Event.microsaccade_filter, min_saccade_amp_deg=MIN_SACCADE_AMP_DEG, min_saccade_dur_ms=MIN_SACCADE_DUR_MS, width_of_image_px=192, hfov=HFOV_DEG)
    print("Summary 3:",event_list.return_list_summary())
    event_list.apply_filter(fixation_packages.event.Event.short_fixation_filter, min_fixation_dur_ms=MIN_FIXATION_DUR_MS)
    print("Summary 4:",event_list.return_list_summary())

    # EXPORT TO JSON
    timestamp_list = fixation_packages.export.create_timestamp_list(event_list)
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
    runner(date_of_url_data=DATE_OF_URL_DATA, pldata_to_load=PLDATA_TO_LOAD, npz_to_load=NPZ_TO_LOAD, world_scene_video_path='./flaskr/fixation/test_data/videos/video.mp4', export_file_path="./flaskr/fixation/export.json", gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR, initial_world_hz=30, desired_world_hz=200)
    print("complete")

if __name__ == "__main__":
    main()