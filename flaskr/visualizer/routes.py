# matt and brian's work

# base
import os

# flask and its plugins
from flask import render_template, session, redirect

# local
from flaskr.visualizer import blueprint
from flaskr.visualizer.methods import *

UPLOAD_FOLDER = 'uploads'

@blueprint.route("/visualizer")
def visualizer():
    upload_path = os.path.join(UPLOAD_FOLDER, session['upload_uuid'])

    eye0_path = os.path.join(upload_path, 'eye0.mp4')
    eye1_path = os.path.join(upload_path, 'eye1.mp4')
    world_path = os.path.join(upload_path, 'world.mp4')
    odo_pldata_path = os.path.join(upload_path, 'odometry.pldata')
    gaze_npz_path = os.path.join(upload_path, 'gaze.npz')

    # This returns a JSON_list, in the refactor this will go to the frontend JS for graph generation, in the form of lists not graphs
    vel_data = generate_velocity_graphs([odo_pldata_path])
    gaze_data = generate_gaze_graph([gaze_npz_path])

    return render_template("visualizer/visualizer.html",
                           eye0_path=eye0_path,
                           eye1_path=eye1_path,
                           world_path=world_path,
                           velocity_timestamps=vel_data[0],
                           linear_0=vel_data[1], linear_1=vel_data[2], linear_2=vel_data[3],
                           angular_0=vel_data[4], angular_1=vel_data[5], angular_2=vel_data[6],
                           left_gaze_timestamps=gaze_data[0], left_norm_pos_x=gaze_data[1], left_norm_pos_y=gaze_data[2],
                           right_gaze_timestamps=gaze_data[3], right_norm_pos_x=gaze_data[4], right_norm_pos_y=gaze_data[5]
                           )

@blueprint.route("/download")
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
def return_to_file_upload():
    session.pop('upload_uuid', None)
    return redirect("/file_upload")
