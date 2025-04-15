# All code in this file is our own work.

# from .fixation_packages import *
try:
    import fixation.fixation_packages as fixation_packages
except ModuleNotFoundError as e:
    try:
        import flaskr.fixation.fixation_packages as fixation_packages
    except ModuleNotFoundError as e:    
        print("Run in console from flaskr/ as:\npython -m fixation.main")
        input("exitting")
        raise e

# from fixation.fixation_packages import *

# import fixation_packages.event
# from fixation.fixation_packages import event
# import fixation_packages.event_list
# import fixation_packages.export
# import fixation_packages.ingestion
# import fixation_packages.gaze_processing
# import fixation_packages.IMU_processing
# # import fixation_packages.lucas_kanade
# import fixation_packages.gridTracking_LUCAS_KANADE_TEST
# import fixation_packages.spatial_average
# import fixation_packages.adaptive_threshold
# import fixation_packages.IMU_processing

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

from flaskr.fixation.constants import *       # import all global constants as defined in constants.py
    

def runner(pldata_to_load, gaze_npz, world_scene_video_path, export_fixation_file_path, export_parameters_file_path, gaze_window_size_ms, polynomial_grade, min_vel_thresh, gain_factor, initial_world_hz, desired_world_hz, world_camera_width, world_camera_height, camera_fov_h, camera_fov_v, imu_flag):
    import inspect
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    ARGUMENT_LIST = [(i, values[i]) for i in args]
    
    gaze_data_dict = fixation_packages.ingestion.generate_gaze_data(gaze_npz)
    
    # Step 1
    # We need one gaze velocity vector, so I'm just gonna average out the left and right eye vectors (based on the length of the min list)
    min_len = min(len(gaze_data_dict["left_norm_pos_x"]), len(gaze_data_dict["left_norm_pos_y"]), len(gaze_data_dict["right_norm_pos_x"]), len(gaze_data_dict["right_norm_pos_y"]))

    # Generate gaze timestamp list to calculate velocity
    gaze_timestamp = fixation_packages.gaze_processing.get_timestamp_list(gaze_data_dict, min_len, "left")


    raw_gaze_vec_ = fixation_packages.gaze_processing.calculate_raw_gaze_vector(gaze_data_dict, x_res=X_RES, y_res=Y_RES)

    savgol_x = fixation_packages.gaze_processing.savgol(raw_gaze_vec_[0], gaze_window_size_ms, polynomial_grade)
    savgol_y = fixation_packages.gaze_processing.savgol(raw_gaze_vec_[1], gaze_window_size_ms, polynomial_grade)
    savgol_gaze_vec = np.array(np.column_stack([savgol_x, savgol_y]))
# THE GAZE VECTOR IS NORMALISED, MUST CONVERT TO PIXEL SPACE

    # Step 2
    v_hat = fixation_packages.gaze_processing.calculateGazeVelocity(savgol_gaze_vec, gaze_timestamp)

    print("Optic flow calculation start using ", end='')
    if(imu_flag):
        print("IMU")
    else:
        print("Lucas-Kanade")

    if(not imu_flag):
    # Step 3*
        global_OF_vec_list = fixation_packages.gridTracking_LUCAS_KANADE_TEST.do_it(world_scene_video_path)  # Needs to be averaged before upsampled
        # TODO: Check timestamp alignment
        # TODO: global_OF_vec_list is a list of vectors produced per frame, do we need to find velocity?

    else:
        pldata_data = fixation_packages.ingestion.read_pldata(pldata_to_load)
        df = pd.DataFrame(pldata_data)
        imu_processor = fixation_packages.IMU_processing.IMU_Processor(df, world_camera_width, world_camera_height, camera_fov_h, camera_fov_v)
        global_OF_vec_list = []
        for i in range(10_000):
            if i % 10000 == 0:
                print(i)
            vec_list = imu_processor.compute_grid_rotational_flow(step=100)
            global_OF_vec_list.append(fixation_packages.spatial_average.calculateGlobalOpticFlowVec(vec_list))
            # print(imu_processor.get_time_at(i+1) - imu_processor.get_time_at(i))
            imu_processor.update()
    print("Optic flow calculation end")

    ############## SAVE THE OUTPUT OF LUCAS-KANADE TO SAVE TIME #################
    # import pickle
    # with open('flaskr/fixation/saved_lucas_kanade_data_entire_dataset', 'wb') as fp:
    #     pickle.dump(vec_list, fp)

    # input("AAA")

    # with open ('./fixation/saved_lucas_kanade_data_111s', 'rb') as fp:
    #     global_OF_vec_list = pickle.load(fp)

    #############################################################################



    global_OF_vec_list = np.array(global_OF_vec_list)     # convert to numpy array
    global_OF_vec_list *= 25


    # Step 4*
    if(imu_flag):
        IMU_RATE = 200
        global_OF_vec_list *= IMU_RATE
        new_vec_list = fixation_packages.spatial_average.linear_upsample_dataset(IMU_RATE, desired_world_hz, global_OF_vec_list)
    else:
        CAMERA_RATE = 25
        global_OF_vec_list *= CAMERA_RATE
        new_vec_list = fixation_packages.spatial_average.linear_upsample_dataset(CAMERA_RATE, desired_world_hz, global_OF_vec_list)

    # Step 5

    DEBUG_OPTIC_FLOW = False
    if DEBUG_OPTIC_FLOW:
        with open(f"{export_fixation_file_path}.txt", "w") as f:
            for i, subarray in enumerate(global_OF_vec_list):
                f.write(f"Array {i}:\n")
                np.savetxt(f, subarray, fmt='%.6f')  # format for 2 decimal places
                f.write("\n")
        return

    v_rel, status_code = fixation_packages.adaptive_threshold.gaze_velocity_correction(v_hat, global_OF_vec_list)

    DEBUG_OPTIC_FLOW = False
    if DEBUG_OPTIC_FLOW:
        with open(f"{export_fixation_file_path}.txt", "w") as f:
            for i, subarray in enumerate(v_rel):
                f.write(f"Array {i}:\n")
                np.savetxt(f, subarray, fmt='%.6f')
                f.write("\n")
        return

    # Step 6
    samples_in_window = fixation_packages.adaptive_threshold.calculate_samples_in_window(200, 300)
    v_thr_list = []
    for i in range(len(new_vec_list)- (samples_in_window-1) ):
        v_thr_list.append(fixation_packages.adaptive_threshold.calculate_v_thr(min_vel_thresh, gain_factor, new_vec_list, i, samples_in_window))

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

    print("Summary 1:",event_list.return_list_summary())
    event_list.consolidate_list()
    print("Summary 2:",event_list.return_list_summary())
    event_list.apply_filter(fixation_packages.event.Event.microsaccade_filter, min_saccade_amp_deg=MIN_SACCADE_AMP_DEG, min_saccade_dur_ms=MIN_SACCADE_DUR_MS, width_of_image_px=192, hfov=HFOV_DEG)
    print("Summary 3:",event_list.return_list_summary())
    event_list.apply_filter(fixation_packages.event.Event.short_fixation_filter, min_fixation_dur_ms=MIN_FIXATION_DUR_MS)
    print("Summary 4:",event_list.return_list_summary())

    # EXPORT TO JSON
    timestamp_list = fixation_packages.export.create_timestamp_list(event_list)
    fixation_packages.export.write_json_to_file(fixation_packages.export.create_json(timestamp_list), export_fixation_file_path)
    fixation_packages.export.write_constants_to_file(ARGUMENT_LIST, export_parameters_file_path)

    print("DONE!")

def main():
    print("starting")
    runner(pldata_to_load=PLDATA_TO_LOAD, npz_to_load=NPZ_TO_LOAD, world_scene_video_path='./fixation/test_data/videos/video.mp4', export_fixation_file_path="./fixation/export/export_fixation.json", export_parameters_file_path="./fixation/export/export_parameters.txt" , gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR, initial_world_hz=30, desired_world_hz=200, world_camera_width=2048, world_camera_height=1536, camera_fov_h=90, camera_fov_v=90, imu_flag=True)
    # runner(date_of_url_data=DATE_OF_URL_DATA, pldata_to_load='odometry1.pldata', npz_to_load=NPZ_TO_LOAD, world_scene_video_path='./fixation/test_data/videos/video3.mp4', export_fixation_file_path="./fixation/export/TEST_IMU_DATA_1.json", export_parameters_file_path="./fixation/export/export_imu1_parameters.txt" , gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR, initial_world_hz=30, desired_world_hz=200, world_camera_width=2048, world_camera_height=1536, camera_fov_h=90, camera_fov_v=90, imu_flag=True)
    # runner(date_of_url_data=DATE_OF_URL_DATA, pldata_to_load='odometry2.pldata', npz_to_load=NPZ_TO_LOAD, world_scene_video_path='./fixation/test_data/videos/video3.mp4', export_fixation_file_path="./fixation/export/TEST_IMU_DATA_2.json", export_parameters_file_path="./fixation/export/export_imu2_parameters.txt" , gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR, initial_world_hz=30, desired_world_hz=200, world_camera_width=2048, world_camera_height=1536, camera_fov_h=90, camera_fov_v=90, imu_flag=True)
    print("complete")

if __name__ == "__main__":
    print("Run in console from flaskr/ as:\npython -m fixation.main")
    main()
