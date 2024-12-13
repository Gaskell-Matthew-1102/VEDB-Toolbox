# All code in this file is our own work.
# Steps 5, 6, 7
import numpy as np
from math import sqrt

def gaze_velocity_correction(gaze_velocity_vector: np.ndarray[2], global_optic_flow: np.ndarray[2]):
    relative_gaze_vel = gaze_velocity_vector - global_optic_flow
    return relative_gaze_vel

# old header: calculate_samples_in_window(sample_list: list[np.ndarray], sample_rate_hz: int, window_size_ms:int):
def calculate_samples_in_window(sample_rate_hz: int, window_size_ms:int):
    """
    THIS FUNCTION MAY BE INACCURATE. THIS DOESN'T DIRECTLY COUNT THE NUMBER OF SAMPLES, JUST DOES BASIC ARITHMETIC. MAY NEED TO REFACTOR FOR ACCURACY
    """

    return int(sample_rate_hz * (window_size_ms / 1000))

def calculate_RMS_of_window(optic_flow_vec_list:list[np.ndarray[2]], start_sample:int, samples_in_window:int):
    summation = 0.0
    for sample in range(samples_in_window):
        o_hat_x = optic_flow_vec_list[start_sample+sample][0][0]
        o_hat_y = optic_flow_vec_list[start_sample+sample][0][1]

        summation += o_hat_x ** 2 + o_hat_y ** 2

    rms = sqrt( (1/samples_in_window) * summation )
    return rms

def calculate_v_thr(v_0, gain, rms):
    return v_0 + gain*rms

def calculate_v_thr(v_0, gain, optic_flow_vec_list:list[np.ndarray[2]], start_sample:int, samples_in_window:int):
    return v_0 + gain*calculate_RMS_of_window(optic_flow_vec_list, start_sample, samples_in_window)

vec1 = np.column_stack( (1, 2) )
vec2 = np.column_stack( (6, 1) )
vec3 = np.column_stack( (0, -1, -10) )
vec4 = np.column_stack( (1, 2, 3) )
vec5 = np.column_stack( (6, 6, 5) )


vec_list = [vec1, vec2, vec3, vec4, vec5]
print(calculate_RMS_of_window(vec_list, 0, 5))
print(calculate_samples_in_window(200, 2000))