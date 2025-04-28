# matt and brian's work

# base
import os
import pathlib


# flask and its plugins
from flask import render_template, session, redirect, send_from_directory, jsonify
from flask_login import login_required

# local
from flaskr.visualizer import blueprint
from flaskr.visualizer.methods import *


from flaskr.fixation.main import runner as fixation_main


UPLOAD_FOLDER = 'uploads'

@blueprint.before_request
@login_required
def setup():
    # create export folder per
    fixation_export_path = os.path.join(os.path.join(UPLOAD_FOLDER, session['upload_uuid']), "export")
    if not os.path.exists(fixation_export_path):
        os.makedirs(fixation_export_path, exist_ok=True)

@blueprint.route("/visualizer")
@login_required
def visualizer():
    if not session['data_submitted'] or not session['videos_submitted']:
        return redirect("/file_upload")

    # base directory for all files
    upload_path = os.path.join(UPLOAD_FOLDER, session['upload_uuid'])
    fixation_export_path = os.path.join(upload_path, "export")

    # paths to all relevant files
    world_path = os.path.join(upload_path, 'world.mp4')
    eye0_path = os.path.join(upload_path, 'eye0.mp4')
    eye1_path = os.path.join(upload_path, 'eye1.mp4')
    odo_pldata_path = os.path.join(upload_path, 'odometry.pldata')
    gaze_npz_path = os.path.join(upload_path, 'gaze.npz')
    world_time_path = os.path.join(upload_path, 'world_timestamps.npy')
    export_json_path = os.path.join(fixation_export_path, "export_fixation.json")
    export_parameters_path = os.path.join(fixation_export_path, "export_fixation_parameters.txt")

    csv_list = list(pathlib.Path(upload_path).glob('*.csv'))

    csv_path = ""
    if len(csv_list) == 1:
        csv_path = csv_list[0]
    elif len(csv_list) == 0:
        print("No CSV files uploaded")
    else:
        print("More than one CSV file uploaded")

    # Start the fixation detection algorithm here

    # video manip., metadata
    world_frame_width, world_frame_height, world_fps = get_data_of_video(world_path)
    eye_frame_width, eye_frame_height, eye_fps = get_data_of_video(eye0_path)

    start_fixation_algorithm(odometry_file=odo_pldata_path,
                             gaze_file=gaze_npz_path,
                             world_video_file=world_path,
                             csv_file=csv_path,
                             eye0_file=eye0_path,
                             eye1_file=eye1_path,
                             export_json_path=export_json_path,
                             export_parameters_path=export_parameters_path,
                             in_args=session["fixation_params"])

    # This returns a JSON_list, in the refactor this will go to the frontend JS for graph generation, in the form of lists not graphs
    vel_data = generate_velocity_graphs([odo_pldata_path, world_time_path])
    gaze_data = generate_gaze_graph([gaze_npz_path, world_time_path])


    # # fixations, paths
    # # EXPORT_JSON_PATH = "flaskr/fixation/export/export_fixation.json"
    # EXPORT_JSON_PATH = f"{EXPORT_FOLDER_PATH}/{SESSION_NAME}.json"
    # # EXPORT_PARAMETERS_PATH = "flaskr/fixation/export/export_parameters.txt"
    # EXPORT_PARAMETER_PATH = f"{EXPORT_FOLDER_PATH}/{SESSION_NAME}_parameters.txt"
    #

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

# grabs the json. needed to make /check_fixation_status work
@blueprint.route('/<uuid>/export/<filename>')
@login_required
def fetch_json(uuid, filename):
    fixed_path = os.path.join('..', UPLOAD_FOLDER)
    upload_path = os.path.join(fixed_path, uuid)
    fixation_export_path = os.path.join(upload_path, "export")

    return send_from_directory(fixation_export_path, filename)

@blueprint.route("/check_fixation_status")
@login_required
def check_fixation_status():
    upload_path = os.path.join(UPLOAD_FOLDER, session['upload_uuid'])
    fixation_export_path = os.path.join(upload_path, "export")
    export_json_path = os.path.join(fixation_export_path, "export_fixation.json")

    # if file doesn't exist, exit this function early
    if not os.path.exists(export_json_path):
        return jsonify(file="")
    
    return jsonify(file=export_json_path.split("\\", 1)[1])

@blueprint.route("/return_to_file_upload")
@login_required
def return_to_file_upload():
    return redirect("/file_upload")
