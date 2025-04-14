# All code in this file is our own work.

# Module to process the gaze data stream
# First, low pass filter using Savitzky-Golay filter with 55ms window length and 3rd grade polynomial
# Steps 1, 2
import numpy as np
from scipy.signal import savgol_filter

# WINDOW_SIZE_MS = 55
# POLYNOMIAL_GRADE = 3

def calculate_raw_gaze_vector(gaze_data_dict, x_res, y_res):
    min_len = min(len(gaze_data_dict["left_norm_pos_x"]), len(gaze_data_dict["left_norm_pos_y"]), len(gaze_data_dict["right_norm_pos_x"]), len(gaze_data_dict["right_norm_pos_y"]))
    raw_gaze_left = np.array([gaze_data_dict["left_norm_pos_x"][0:min_len], gaze_data_dict["left_norm_pos_y"][0:min_len]])
    raw_gaze_right = np.array([gaze_data_dict["right_norm_pos_x"][0:min_len], gaze_data_dict["right_norm_pos_y"][0:min_len]])

    # Convert to pixel space

    # The current approach just averages the left and right eyes, and trims the length of the returned list to be the same as the length of the shorter eye
    # raw_gaze_vec = np.array([np.mean([raw_gaze_left[0], raw_gaze_right[0]], 0)*x_res, np.mean([raw_gaze_left[1], raw_gaze_right[1]], 0)*y_res])
    # return raw_gaze_vec

    # This approach just returns the left eye gaze data, as it's actually normalized
    raw_gaze_left = np.array([raw_gaze_left[0]*x_res, raw_gaze_left[1]*y_res])
    return raw_gaze_left


# Wrapper function for Savitzky-Golay filter with specified parameters set as default arguments
def savgol(input, window_length, polynomial_grade) -> np.array:
    output = savgol_filter(input, window_length, polynomial_grade)
    return output

# Returns a np.array of calculated gaze velocities in pixels/sec from the filtered gaze data
def calculateGazeVelocity(input_pos:np.array, input_time:np.array) -> np.array:
    # workingList = np.array([])
    # for i in range(len(input) - 1):
    #     print(i)
    #     workingList = np.append(workingList, input[i+1] - input[i])
    # a = np.diff(input)
    
    return np.divide(np.diff(input_pos, axis=0), np.diff(input_time)[:, np.newaxis])

# Returns an np.array of timestamps
def get_timestamp_list(gaze_data_dict, min_len, eye):
    if(eye == "left"):
        return np.array(gaze_data_dict["left_timestamps"][0:min_len])
    elif(eye == "right"):
        return np.array(gaze_data_dict["right_timestamps"][0:min_len])
    elif(eye == "both"):
        return np.mean([gaze_data_dict["left_timestamps"][0:min_len], gaze_data_dict["right_timestamps"][0:min_len]], axis=0)
