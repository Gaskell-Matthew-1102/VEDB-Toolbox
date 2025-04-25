# matt and brian's work

# base
import os

# flask and its plugins
from flask import render_template, session, redirect, send_from_directory
from flask_login import login_required

# pip
import plotly.io as pio
import plotly.graph_objects as go

# local
from flaskr.visualizer import blueprint
from flaskr.visualizer.methods import *

import pathlib

UPLOAD_FOLDER = 'uploads'

@blueprint.route("/visualizer")
@login_required
def visualizer():
    if not session['data_submitted'] or not session['videos_submitted']:
        return redirect("/file_upload")

    # base directory for all files
    upload_path = os.path.join(UPLOAD_FOLDER, session['upload_uuid'])

    # paths to all relevant files
    world_path = os.path.join(upload_path, 'world.mp4')
    eye0_path = os.path.join(upload_path, 'eye0.mp4')
    eye1_path = os.path.join(upload_path, 'eye1.mp4')
    odo_pldata_path = os.path.join(upload_path, 'odometry.pldata')
    gaze_npz_path = os.path.join(upload_path, 'gaze.npz')
    world_time_path = os.path.join(upload_path, 'world_timestamps.npy')
    csv_list = list(pathlib.Path(upload_path).glob('*.csv'))

    csv_path = ""
    if len(csv_list) == 1:
        csv_path = csv_list[0]
    elif len(csv_list) == 0:
        print("No CSV files uploaded")
    else:
        print("More than one CSV file uploaded")

    # Start the fixation detection algorithm here
    # start_fixation_algorithm(odometry_file=odo_pldata_path, gaze_file=gaze_npz_path, world_video_file=world_path, csv_file=csv_path, eye0_file=eye0_path, eye1_file=eye1_path, in_args=???, )

    # This returns a JSON_list, in the refactor this will go to the frontend JS for graph generation, in the form of lists not graphs
    vel_data = generate_velocity_graphs([odo_pldata_path, world_time_path])
    gaze_data = generate_gaze_graph([gaze_npz_path, world_time_path])

    # video manip., metadata
    world_frame_width, world_frame_height, world_fps = get_data_of_video(world_path)
    eye_frame_width, eye_frame_height, eye_fps = get_data_of_video(eye0_path)

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

    return render_template("visualizer/visualizer.html",
                           world_frame_width=world_frame_width, world_frame_height=world_frame_height,
                           eye_frame_width=eye_frame_width, eye_frame_height=eye_frame_height,

                           velocity_timestamps=vel_data[0],
                           linear_0=vel_data[1], linear_1=vel_data[2], linear_2=vel_data[3],
                           angular_0=vel_data[4], angular_1=vel_data[5], angular_2=vel_data[6],
                           
                           left_gaze_timestamps=gaze_data[0], left_norm_pos_x=gaze_data[1], left_norm_pos_y=gaze_data[2],
                           right_gaze_timestamps=gaze_data[3], right_norm_pos_x=gaze_data[4], right_norm_pos_y=gaze_data[5]
                           )

@blueprint.route('/fetch/<filename>')
@login_required
def fetch(filename):
    fixed_path = os.path.join('..', UPLOAD_FOLDER)
    session_root = os.path.join(fixed_path, session['upload_uuid'])
    return send_from_directory(session_root, filename)

@blueprint.route("/download")
@login_required
def download_graphs():
    if request.method == "POST":
        graphs = request.get_json()
        linear = graphs["lin_graph"]
        angular = graphs["ang_graph"]

        linear_graph = go.Figure(linear)
        angular_graph = go.Figure(angular)

        if not os.path.exists("graphs"):
            os.mkdir("graphs")

        fig_numbers = get_fig_numbers()
        pio.write_image(linear_graph, "images/linear_graph" + str(fig_numbers[0]) + ".png")
        pio.write_image(angular_graph, "images/angular_graph" + str(fig_numbers[1]) + ".png")



@blueprint.route("/return_to_file_upload")
@login_required
def return_to_file_upload():
    session.pop('upload_uuid', None)
    return redirect("/file_upload")


###################### TEST ROUTES ###########################
@blueprint.route("/visualizer_test")
def visualizer_test():
    # base directory for all files
    upload_path = os.path.join(UPLOAD_FOLDER, "test")
    
    # paths to all relevant files
    world_path = os.path.join(upload_path, 'world.mp4')
    eye0_path = os.path.join(upload_path, 'eye0.mp4')
    eye1_path = os.path.join(upload_path, 'eye1.mp4')
    odo_pldata_path = os.path.join(upload_path, 'odometry.pldata')
    gaze_npz_path = os.path.join(upload_path, 'gaze.npz')
    world_time_path = os.path.join(upload_path, 'world_timestamps.npy')

    # This returns a JSON_list, in the refactor this will go to the frontend JS for graph generation, in the form of lists not graphs
    vel_data = generate_velocity_graphs([odo_pldata_path, world_time_path])
    gaze_data = generate_gaze_graph([gaze_npz_path, world_time_path])
    
    # video manip., metadata
    world_frame_width, world_frame_height, world_fps = get_data_of_video(world_path)
    eye_frame_width, eye_frame_height, eye_fps = get_data_of_video(eye0_path)

    return render_template("visualizer/visualizer_test.html",
                           world_frame_width=world_frame_width, world_frame_height=world_frame_height,
                           eye_frame_width=eye_frame_width, eye_frame_height=eye_frame_height,
                           
                           velocity_timestamps=vel_data[0],
                           linear_0=vel_data[1], linear_1=vel_data[2], linear_2=vel_data[3],
                           angular_0=vel_data[4], angular_1=vel_data[5], angular_2=vel_data[6],
                           
                           left_gaze_timestamps=gaze_data[0], left_norm_pos_x=gaze_data[1], left_norm_pos_y=gaze_data[2],
                           right_gaze_timestamps=gaze_data[3], right_norm_pos_x=gaze_data[4], right_norm_pos_y=gaze_data[5]
                           )

@blueprint.route('/fetch_test/<filename>')
def fetch_test(filename):
    fixed_path = os.path.join('..', UPLOAD_FOLDER)
    session_root = os.path.join(fixed_path, "test")
    return send_from_directory(session_root, filename)
