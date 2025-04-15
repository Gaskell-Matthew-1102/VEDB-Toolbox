import cv2
import time
import math
import numpy as np
import json
import os
from fixation_packages.ingestion import *
from fixation_packages.gaze_processing import get_timestamp_list, calculateGazeVelocity, calculate_raw_gaze_vector, savgol

def visualize_session(eye_video1_path, eye_video2_path, world_video_path, start_time, end_time, gaze_vel_list):
    """
    Visualizes two eye videos and one world video between start_time and end_time.

    Parameters:
      eye_video1_path (str): Path to the first eye video.
      eye_video2_path (str): Path to the second eye video.
      world_video_path (str): Path to the world (scene) video.
      start_time (float): Start time in seconds.
      end_time (float): End time in seconds.
    """
    # Open the videos
    cap_eye1 = cv2.VideoCapture(eye_video1_path)
    cap_eye2 = cv2.VideoCapture(eye_video2_path)
    cap_world = cv2.VideoCapture(world_video_path)

    # Get frame rates
    fps_eye1   = 120
    fps_eye2   = 120
    fps_world  = 25

    # Calculate starting frame for each video
    start_frame_eye1 = int(start_time * fps_eye1)
    start_frame_eye2 = int(start_time * fps_eye2)
    start_frame_world = int(start_time * fps_world)

    # Seek to the start frame of each video
    cap_eye1.set(cv2.CAP_PROP_POS_FRAMES, start_frame_eye1)
    cap_eye2.set(cv2.CAP_PROP_POS_FRAMES, start_frame_eye2)
    cap_world.set(cv2.CAP_PROP_POS_FRAMES, start_frame_world)

    # Calculate ending frame index for each video
    end_frame_eye1 = int(end_time * fps_eye1)
    end_frame_eye2 = int(end_time * fps_eye2)
    end_frame_world = int(end_time * fps_world)

    while True:
        # Get current frame positions
        pos_eye1 = cap_eye1.get(cv2.CAP_PROP_POS_FRAMES)
        pos_eye2 = cap_eye2.get(cv2.CAP_PROP_POS_FRAMES)
        pos_world = cap_world.get(cv2.CAP_PROP_POS_FRAMES)

        # Stop if any video reaches its end frame
        if pos_eye1 >= end_frame_eye1 or pos_eye2 >= end_frame_eye2 or pos_world >= end_frame_world:
            print("a")
            break

        ret1, frame_eye1 = cap_eye1.read()
        ret2, frame_eye2 = cap_eye2.read()
        ret_world, frame_world = cap_world.read()

        frame_eye1 = cv2.rotate(frame_eye1, cv2.ROTATE_180)

        if not ret1 or not ret2 or not ret_world:
            print("b")
            break

        # Optionally, resize the videos for a better visualization
        # For this example, assume the eye videos have the same resolution.
        h_eye, w_eye = frame_eye1.shape[:2]
        h_world, w_world = frame_world.shape[:2]

        # Stack eye videos vertically:
        eyes_combined = cv2.vconcat([frame_eye1, frame_eye2])
        
        # Resize world video to match the vertical height of the stacked eye videos
        eyes_height = eyes_combined.shape[0]
        scale_factor = eyes_height / h_world
        new_world_width = int(w_world * scale_factor)
        frame_world_resized = cv2.resize(frame_world, (new_world_width, eyes_height))

        # Combine horizontally:
        combined = cv2.hconcat([eyes_combined, frame_world_resized])

        cv2.imshow("Session Visualization", combined)
        frame_num = cap_eye1.get(cv2.CAP_PROP_POS_FRAMES)
        # cv2.putText(combined, f"Frame {frame_num} gaze vel: {gaze_vel_list[frame_num]}", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)  # frame
        # Wait appropriate time (using the world video fps for timing)
        key = cv2.waitKey(int(1000/fps_world))
        if key == ord('q'):
            break

    # Clean up
    cap_eye1.release()
    cap_eye2.release()
    cap_world.release()
    cv2.destroyAllWindows()

def read_json_to_array(file_path: str) -> np.ndarray:
    """
    Reads a JSON file with a structure like [[0.0, 1.0], [2.0, 2.5], ...]
    and returns a numpy array.

    Parameters:
        file_path (str): Path to the JSON file.
        
    Returns:
        np.ndarray: A numpy array containing the data.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return np.array(data)

# Example usage:
if __name__ == "__main__":
    OUTPUT_FOLDER_PATH = "fixation\\test_data\\VIDEO_DUMP"

    data = read_json_to_array("fixation\\export\\export_fixation.json")

    eye_video1_path = "fixation\\test_data\\videos\\473417-eye0_blur.mp4"
    eye_video2_path = "fixation\\test_data\\videos\\473419-eye1_blur.mp4"
    world_video_path = "fixation\\test_data\\videos\\video.mp4"


    # gaze_data_dict = generate_gaze_data("fixation\\test_data\\2023_06_01_18_47_34\\processedGaze\\gaze.npz")
    # min_len = min(len(gaze_data_dict["left_norm_pos_x"]), len(gaze_data_dict["left_norm_pos_y"]), len(gaze_data_dict["right_norm_pos_x"]), len(gaze_data_dict["right_norm_pos_y"]))
    # gaze_timestamp = get_timestamp_list(gaze_data_dict, min_len, "left")
    # raw_gaze_vec_ = calculate_raw_gaze_vector(gaze_data_dict, x_res=400, y_res=400)
    # savgol_x = savgol(raw_gaze_vec_[0], 55, 3)
    # savgol_y = savgol(raw_gaze_vec_[1], 55, 3)
    # savgol_gaze_vec = np.array(np.column_stack([savgol_x, savgol_y]))
    # v_hat = calculateGazeVelocity(savgol_gaze_vec, gaze_timestamp)



    for sample_i in range(data.size-1):
        start_time = data[sample_i][0]
        end_time = data[sample_i][1]
        
        # start_time = data[sample_i][1]
        # end_time = data[sample_i+1][0]

        if end_time - start_time < 0.15:
            continue
        visualize_session(eye_video1_path, eye_video2_path, world_video_path, start_time, end_time, None)