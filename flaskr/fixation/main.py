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

TEMP_COOL_ARGS = ('uploads\\a50a09b0-4d03-4709-8834-5f9f3f9f6ca5\\odometry.pldata', 'uploads\\a50a09b0-4d03-4709-8834-5f9f3f9f6ca5\\gaze.npz', 'uploads\\a50a09b0-4d03-4709-8834-5f9f3f9f6ca5\\world.mp4', './fixation/export/export_fixation.json', './fixation/export/export_fixation_parameters.txt', 55, 300, 3, 750, 0.8, 25, 400, 400, 2048, 1536, 90, 90, True, 1.0, 10, 110, 70)

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

try:
    from flaskr.fixation.constants import *       # import all global constants as defined in constants.py
except ModuleNotFoundError:
    try:
        from fixation.constants import *       # import all global constants as defined in constants.py
    except ModuleNotFoundError as e:
        raise e

def runner(pldata_to_load, gaze_npz, world_scene_video_path, export_fixation_file_path, export_parameters_file_path, gaze_window_size_ms, polynomial_grade, adap_window_size_ms, min_vel_thresh, gain_factor, desired_world_hz, eye_camera_width_px, eye_camera_height_px, world_camera_width, world_camera_height, world_camera_fov_h, world_camera_fov_v, imu_flag, min_saccade_amp_deg, min_saccade_dur_ms, eye_hfov, min_fixation_dur_ms):
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
    raw_gaze_vec_ = fixation_packages.gaze_processing.calculate_raw_gaze_vector(gaze_data_dict, eye_camera_width_px, eye_camera_height_px)

    upsampled_timestamps, upsampled_raw_gaze = fixation_packages.spatial_average.linear_interpolate(gaze_timestamp, raw_gaze_vec_.transpose(), 120, 200)
    upsampled_raw_gaze = upsampled_raw_gaze.transpose()

    print("LEN:", len(upsampled_raw_gaze[0]))

    savgol_x = fixation_packages.gaze_processing.savgol(upsampled_raw_gaze[0], gaze_window_size_ms, polynomial_grade)
    savgol_y = fixation_packages.gaze_processing.savgol(upsampled_raw_gaze[1], gaze_window_size_ms, polynomial_grade)
    savgol_gaze_vec = np.array(np.column_stack([savgol_x, savgol_y]))
    # THE GAZE VECTOR IS NORMALISED, MUST CONVERT TO PIXEL SPACE

    # Step 2
    v_hat = fixation_packages.gaze_processing.calculateGazeVelocity(savgol_gaze_vec, upsampled_timestamps)

    print("Optic flow calculation start using ", end='')
    if(imu_flag):
        print("IMU")
    else:
        print("Lucas-Kanade")

    if(not imu_flag):
    # Step 3*
        global_OF_vec_list = fixation_packages.gridTracking_LUCAS_KANADE_TEST.do_it(world_scene_video_path, 0.25)  # Needs to be averaged before upsampled
        # TODO: Check timestamp alignment
        # TODO: global_OF_vec_list is a list of vectors produced per frame, do we need to find velocity?

    # Can downsample the input to Lucas Kanade 
    # Look in fileio.load_video (size parameter)
    else:
        pldata_data = fixation_packages.ingestion.read_pldata(pldata_to_load)
        df = pd.DataFrame(pldata_data)
        imu_processor = fixation_packages.IMU_processing.IMU_Processor(df, world_camera_width, world_camera_height, world_camera_fov_h, world_camera_fov_v)
        global_OF_vec_list = []
        print(len(df))      # = 332691
        for i in range(len(df)-2):      # passes here, crashes when len(df)-1
            if i % 10000 == 0:
                print(i)
            vec_list = imu_processor.compute_grid_rotational_flow(step=100)
            global_OF_vec_list.append(fixation_packages.spatial_average.calculateGlobalOpticFlowVec(vec_list))
            # print(imu_processor.get_time_at(i+1) - imu_processor.get_time_at(i))
            try:
                imu_processor.update()
            except IndexError as e:
                print("Crashed on i =", i)
                raise e
    print("Optic flow calculation end")

    ############## SAVE THE OUTPUT OF LUCAS-KANADE TO SAVE TIME #################
    # import pickle
    # with open('./fixation/2022_08_25_10_18_37_saved_lucas_kanade_data_entire_dataset', 'wb') as fp:
    #     pickle.dump(global_OF_vec_list, fp)

    # input("AAA")

    # import pickle
    # with open ('./fixation/2022_08_25_10_18_37_saved_lucas_kanade_data_entire_dataset', 'rb') as fp:
    #     global_OF_vec_list = pickle.load(fp)

    #############################################################################


    global_OF_vec_list = np.array(global_OF_vec_list)     # convert to numpy array


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
    v_rel, status_code = fixation_packages.adaptive_threshold.gaze_velocity_correction(v_hat, new_vec_list)

    # Step 6
    samples_in_window = fixation_packages.adaptive_threshold.calculate_samples_in_window(200, adap_window_size_ms)
    v_thr_list = []
    for i in range(len(new_vec_list)- (samples_in_window-1) ):
        v_thr_list.append(fixation_packages.adaptive_threshold.calculate_v_thr(min_vel_thresh, gain_factor, new_vec_list, i, samples_in_window))

    # Begin classification
    temp_event_list = []
    for sample_i in range(min(len(v_rel), len(v_thr_list))-1):
        rel_gaze_vel = np.linalg.norm(np.array([v_rel[sample_i][0], v_rel[sample_i][1]]))

        first_timestamp = upsampled_timestamps[sample_i]
        second_timestamp = upsampled_timestamps[sample_i+1]

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
    event_list.apply_filter(fixation_packages.event.Event.microsaccade_filter, min_saccade_amp_deg=min_saccade_amp_deg, min_saccade_dur_ms=min_saccade_dur_ms, width_of_image_px=eye_camera_width_px, eye_hfov=eye_hfov)
    print("Summary 3:",event_list.return_list_summary())
    event_list.apply_filter(fixation_packages.event.Event.short_fixation_filter, min_fixation_dur_ms=min_fixation_dur_ms)
    print("Summary 4:",event_list.return_list_summary())

    # sanity rate checks (gaze then imu then world)
    GAZE_RATE = 1 / (upsampled_timestamps[1] - upsampled_timestamps[0])
    WORLD_RATE = 1 / (new_vec_list.size / global_OF_vec_list.size)

    print(GAZE_RATE, WORLD_RATE)


    # EXPORT TO JSON
    timestamp_list = fixation_packages.export.create_timestamp_list(event_list)
    fixation_packages.export.write_json_to_file(fixation_packages.export.create_json(timestamp_list), export_fixation_file_path)
    fixation_packages.export.write_constants_to_file(ARGUMENT_LIST, export_parameters_file_path)

    print("DONE!")

def main():
    print("starting")
    # runner(pldata_to_load=PLDATA_TO_LOAD, gaze_npz=NPZ_TO_LOAD, world_scene_video_path='./fixation/test_data/videos/video.mp4', export_fixation_file_path="./fixation/export/export_fixation.json", export_parameters_file_path="./fixation/export/export_parameters.txt" , gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR, initial_world_hz=25, desired_world_hz=200, eye_camera_width_px=X_RES, eye_camera_height_px=Y_RES, world_camera_width=2048, world_camera_height=1536, world_camera_fov_h=90, world_camera_fov_v=90, imu_flag=False, min_saccade_amp_deg=MIN_SACCADE_AMP_DEG, min_saccade_dur_ms=MIN_SACCADE_DUR_MS, eye_hfov=EYE_HFOV_DEG, min_fixation_dur_ms=MIN_FIXATION_DUR_MS)
    runner(pldata_to_load="./fixation/test_data/viewer_input2/data/odometry.pldata", 
            gaze_npz="./fixation/test_data/viewer_input2/data/gaze.npz", 
            world_scene_video_path='./fixation/test_data/viewer_input2/video/worldPrivate.mp4', 
            export_fixation_file_path="./fixation/export/export_fixation.json", 
            export_parameters_file_path="./fixation/export/export_parameters.txt" , 
            gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, 
            polynomial_grade=POLYNOMIAL_GRADE, 
            adap_window_size_ms=ADAP_WINDOW_SIZE_MS,
            min_vel_thresh=MIN_VEL_THRESH, 
            gain_factor=GAIN_FACTOR, 
            desired_world_hz=200, 
            eye_camera_width_px=X_RES,
            eye_camera_height_px=Y_RES,
            world_camera_width=2048,
            world_camera_height=1536,
            world_camera_fov_h=90,
            world_camera_fov_v=90,
            imu_flag=False,
            min_saccade_amp_deg=MIN_SACCADE_AMP_DEG,
            min_saccade_dur_ms=MIN_SACCADE_DUR_MS,
            eye_hfov=EYE_HFOV_DEG, 
            min_fixation_dur_ms=MIN_FIXATION_DUR_MS
        )
    # runner(date_of_url_data=DATE_OF_URL_DATA, pldata_to_load='odometry1.pldata', npz_to_load=NPZ_TO_LOAD, world_scene_video_path='./fixation/test_data/videos/video3.mp4', export_fixation_file_path="./fixation/export/TEST_IMU_DATA_1.json", export_parameters_file_path="./fixation/export/export_imu1_parameters.txt" , gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR, initial_world_hz=30, desired_world_hz=200, world_camera_width=2048, world_camera_height=1536, camera_fov_h=90, camera_fov_v=90, imu_flag=True)
    # runner(date_of_url_data=DATE_OF_URL_DATA, pldata_to_load='odometry2.pldata', npz_to_load=NPZ_TO_LOAD, world_scene_video_path='./fixation/test_data/videos/video3.mp4', export_fixation_file_path="./fixation/export/TEST_IMU_DATA_2.json", export_parameters_file_path="./fixation/export/export_imu2_parameters.txt" , gaze_window_size_ms=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE, min_vel_thresh=MIN_VEL_THRESH, gain_factor=GAIN_FACTOR, initial_world_hz=30, desired_world_hz=200, world_camera_width=2048, world_camera_height=1536, camera_fov_h=90, camera_fov_v=90, imu_flag=True)
    print("complete")

"""
Example input: 
    {
        "gaze_window_size" : "55",
        "polynomial_grade" : 3,
        ...
    }
"""
def parse_viewer_arguments(arg_dict:dict) -> tuple:
    """
    Converts the argument dictionary passed from the viewer into the tuple form that the algorithm takes in.
    """
    try:
        odometry_path = str(arg_dict['odometry_path'])
        gaze_path = str(arg_dict['gaze_path'])
        world_video_path = str(arg_dict['world_video_path'])
        export_json_path = str(arg_dict['export_json_path'])
        export_parameters_path = str(arg_dict['export_parameters_path'])

        gaze_window_size_ms = int(arg_dict['gaze_window_size'])
        adap_window_size_ms = int(arg_dict['adap_window_size_ms'])
        polynomial_grade = int(arg_dict['polynomial_grade'])
        minimum_vel_thresh = int(arg_dict['min_vel_thresh'])
        gain = float(arg_dict['gain'])
        eye_camera_x_px = int(arg_dict['eye_camera_x_px'])
        eye_camera_y_px = int(arg_dict['eye_camera_y_px'])
        eye_horiz_fov = int(arg_dict['eye_horiz_fov'])
        world_camera_fov_horizontal = int(arg_dict['world_camera_fov_horiz'])
        world_camera_fov_vertical = int(arg_dict['world_camera_fov_vert'])
        world_camera_x_px = int(arg_dict['world_camera_x_px'])
        world_camera_y_px = int(arg_dict['world_camera_y_px'])
        desired_hz = int(arg_dict['desired_hz'])
        min_saccade_amp_deg = float(arg_dict['min_saccade_amp_deg'])
        min_saccade_dur_ms = int(arg_dict['min_saccade_dur_ms'])
        min_fix_dur_ms = int(arg_dict['min_fix_dur_ms'])
        imu_flag = bool(arg_dict['imu_flag'])
    except Exception as e:
        print("Unable to parse viewer arguments")
        raise e
    
    args = (
        odometry_path, 
        gaze_path, 
        world_video_path, 
        export_json_path, 
        export_parameters_path, 
        gaze_window_size_ms, 
        polynomial_grade, 
        adap_window_size_ms,
        minimum_vel_thresh, 
        gain, 
        desired_hz, 
        eye_camera_x_px, 
        eye_camera_y_px, 
        world_camera_x_px, 
        world_camera_y_px, 
        world_camera_fov_horizontal, 
        world_camera_fov_vertical, 
        imu_flag, 
        min_saccade_amp_deg, 
        min_saccade_dur_ms, 
        eye_horiz_fov, 
        min_fix_dur_ms
    )
    return args

if __name__ == "__main__":
    print("Run in console from flaskr/ as:\npython -m fixation.main")
    main()
