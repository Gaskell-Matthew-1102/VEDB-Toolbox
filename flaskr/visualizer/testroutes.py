# base
import os

# flask and its plugins
from flask import render_template, send_from_directory

# local
from flaskr.visualizer import blueprint
from flaskr.visualizer.methods import *

UPLOAD_FOLDER = 'uploads'

@blueprint.route("/visualizer_test")
def visualizer_test():
    # base directory for all files
    upload_path = os.path.join(UPLOAD_FOLDER, "test")

    # paths to all relevant files
    odo_pldata_path = os.path.join(upload_path, 'odometry.pldata')
    gaze_npz_path = os.path.join(upload_path, 'gaze.npz')

    # This returns a JSON_list, in the refactor this will go to the frontend JS for graph generation, in the form of lists not graphs
    vel_data = generate_velocity_graphs([odo_pldata_path])
    gaze_data = generate_gaze_graph([gaze_npz_path])


    # # fixations, paths
    # # EXPORT_JSON_PATH = "flaskr/fixation/export/export_fixation.json"
    # EXPORT_JSON_PATH = f"{EXPORT_FOLDER_PATH}/{SESSION_NAME}.json"
    # # EXPORT_PARAMETERS_PATH = "flaskr/fixation/export/export_parameters.txt"
    # EXPORT_PARAMETER_PATH = f"{EXPORT_FOLDER_PATH}/{SESSION_NAME}_parameters.txt"
    #
    # # Let's start the fixation algorithm here
    # fix_det_args = (
    #     odometry_file, gaze_file,
    #     world_video_file, EXPORT_JSON_PATH,
    #     EXPORT_PARAMETER_PATH,
    #     55, 3, 750, 0.8, world_fps, 200, eye_frame_width, eye_frame_height, world_frame_width, world_frame_height, 90,
    #     90, imu_flag,
    #     1.0, 10, 110, 70
    # )
    #
    # start_fixation_algorithm(fix_det_args)

    return render_template("visualizer/visualizer_test.html",
                           velocity_timestamps=vel_data[0],
                           linear_0=vel_data[1], linear_1=vel_data[2], linear_2=vel_data[3],
                           angular_0=vel_data[4], angular_1=vel_data[5], angular_2=vel_data[6],
                           left_gaze_timestamps=gaze_data[0], left_norm_pos_x=gaze_data[1], left_norm_pos_y=gaze_data[2],
                           right_gaze_timestamps=gaze_data[3], right_norm_pos_x=gaze_data[4], right_norm_pos_y=gaze_data[5]
                           )

@blueprint.route('/fetch_test/<filename>')
def fetch(filename):
    fixed_path = os.path.join('..', UPLOAD_FOLDER)
    session_root = os.path.join(fixed_path, "test")
    return send_from_directory(session_root, filename)