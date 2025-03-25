# All code in this file is our own work.
# Steps 5, 6, 7
import numpy as np
from math import sqrt

# Returns a tuple: (resulting vector calculated by subtracting the global optic flow from the gaze velocity, status code)
def gaze_velocity_correction(gaze_velocity_vector: np.ndarray[2], global_optic_flow: np.ndarray[2]) -> tuple[np.ndarray[2], int]:
    gaze_vec_len = len(gaze_velocity_vector)
    opt_flow_len = len(global_optic_flow)

    print(gaze_vec_len)
    print(opt_flow_len)


    min_len = min(gaze_vec_len, opt_flow_len)
    status_code = -1

    if(gaze_vec_len == opt_flow_len):
        status_code = 0
    elif(gaze_vec_len > opt_flow_len):
        status_code = 1
        # temp_x = gaze_velocity_vector[0][0:min_len]
        # temp_y = gaze_velocity_vector[1][0:min_len]
        # gaze_velocity_vector = np.array([temp_x, temp_y])
    else:
        status_code = 2
        # temp_x = global_optic_flow[0][0:min_len]
        # temp_y = global_optic_flow[1][0:min_len]
        # global_optic_flow = np.array([temp_x, temp_y])

    # print(gaze_velocity_vector[0:min_len,:])
    # print(global_optic_flow[0:min_len,:])
    relative_gaze_vel = gaze_velocity_vector[0:min_len,:] - global_optic_flow[0:min_len,:]
    return (relative_gaze_vel, status_code)
    # return np.linalg.norm(relative_gaze_vel)

# old header: calculate_samples_in_window(sample_list: list[np.ndarray], sample_rate_hz: int, window_size_ms:int):
def calculate_samples_in_window(sample_rate_hz: int, window_size_ms:int):
    """
    THIS FUNCTION MAY BE INACCURATE. THIS DOESN'T DIRECTLY COUNT THE NUMBER OF SAMPLES, JUST DOES BASIC ARITHMETIC. MAY NEED TO REFACTOR FOR ACCURACY
    """

    return int(sample_rate_hz * (window_size_ms / 1000))

def calculate_RMS_of_window(optic_flow_vec_list:np.ndarray[np.ndarray[2]], start_sample:int, samples_in_window:int):
    summation = 0.0
    for sample in range(samples_in_window):
        o_hat_x = optic_flow_vec_list[start_sample+sample][0]
        o_hat_y = optic_flow_vec_list[start_sample+sample][1]

        summation += o_hat_x ** 2 + o_hat_y ** 2

    rms = sqrt( (1/samples_in_window) * summation )
    return rms

def calculate_v_thr(v_0, gain, rms):
    return v_0 + gain*rms

def calculate_v_thr(v_0, gain, optic_flow_vec_list:list[np.ndarray[2]], start_sample:int, samples_in_window:int):
    return v_0 + gain*calculate_RMS_of_window(optic_flow_vec_list, start_sample, samples_in_window)