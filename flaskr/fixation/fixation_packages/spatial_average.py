# All code in this file is our own work.

import numpy as np

def calculateGlobalOpticFlowVec(local_vecs: list[np.ndarray[2]]):
    if len(local_vecs) == 0:
        return np.array([0, 0])
    return np.average(local_vecs, axis=0)


def linear_upsample(initial_Hz: float, desired_Hz: float, vec_1: np.ndarray[2], vec_2: np.ndarray[2]):
    """
    Linearly interpolates points between vec_1 and vec_2
    
    Returns:
        List of vectors(np.ndarray) containing vec_1, all interpolated vectors, and vec_2
    """

    vec_list = []
    vec_list.append(vec_1)
    if(initial_Hz == desired_Hz):
        vec_list.append(vec_2)
        return vec_list
    if(desired_Hz < initial_Hz):
        raise ValueError("Downsampling unsupported")

    # initial_time_step = (1/initial_Hz)
    # desired_time_step = (1/desired_Hz)

    interpolated_point_count = int(desired_Hz / initial_Hz) - 2

    diff_vec = (vec_2 - vec_1)
    step_x = diff_vec[0] / (interpolated_point_count+1)
    step_y = diff_vec[1] / (interpolated_point_count+1)
    # step_z = diff_vec[2] / (interpolated_point_count+1)

    for i in range(interpolated_point_count):
        temp_x_comp = vec_1[0] + step_x * (i+1)
        temp_y_comp = vec_1[1] + step_y * (i+1)
        # temp_z_comp = vec_1[0][2] + step_z * (i+1)

        temp_vec = np.column_stack((temp_x_comp, temp_y_comp))[0]
        # temp_vec = np.column_stack((temp_x_comp, temp_y_comp, temp_z_comp))
        vec_list.append(temp_vec)

    vec_list.append(vec_2)
    return vec_list

def linear_upsample_dataset(initial_Hz: float, desired_Hz: float, vec_list: list[np.ndarray[2]]):
    sample_count = len(vec_list)
    if(sample_count == 0):
        raise ValueError("Empty vec_list")
    total_list = []
    temp = []
    for sample_i in range(sample_count - 1):
        # total_list.extend(linear_upsample(initial_Hz, desired_Hz, vec_list[sample_i], vec_list[sample_i]))
        total_list.extend(linear_upsample(initial_Hz, desired_Hz, vec_list[sample_i], vec_list[sample_i+1]))
        temp = total_list.pop()
    total_list.append(temp)
    return np.array(total_list)