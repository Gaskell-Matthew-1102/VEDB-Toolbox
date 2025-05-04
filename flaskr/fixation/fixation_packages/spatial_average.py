# All code in this file is our own work.

import numpy as np

def calculateGlobalOpticFlowVec(local_vecs: list[np.ndarray[2]]):
    if len(local_vecs) == 0:
        return np.array([0, 0])
    return np.average(local_vecs, axis=0)

# This function was written by ChatGPT
def linear_upsample(initial_Hz: float, desired_Hz: float, vec_1: np.ndarray, vec_2: np.ndarray):
    # If sampling rates are equal, no upsampling is needed.
    if initial_Hz == desired_Hz:
        return [vec_1, vec_2]
    if desired_Hz < initial_Hz:
        raise ValueError("Downsampling unsupported")
    
    # Total duration of the interval between vec_1 and vec_2.
    T = 1.0 / initial_Hz
    # Desired time step between samples.
    desired_step = 1.0 / desired_Hz
    
    # Generate sample times starting at 0 with step desired_step.
    # We use np.arange to get times in [0, T). We then append T to guarantee the last sample.
    times = np.arange(0, T, desired_step)
    # If T is not already included as the last time point, append it.
    if times.size == 0 or times[-1] < T:
        times = np.append(times, T)
    
    # Interpolate using the relative time (alpha = t / T).
    vec_list = [(1 - (t / T)) * vec_1 + (t / T) * vec_2 for t in times]    
    return vec_list

def linear_upsample_dataset(initial_Hz: float, desired_Hz: float, vec_list: list[np.ndarray]):
    if vec_list is None or vec_list.size == 0:
        raise ValueError("Empty vec_list")
    
    total_list = []
    
    for i in range(len(vec_list) - 1):
        segment = linear_upsample(initial_Hz, desired_Hz, vec_list[i], vec_list[i+1])
        if i > 0:
            # Omit the first element of this segment to prevent duplicates.
            segment = segment[1:]
        total_list.extend(segment)
    
    return np.array(total_list)

def linear_upsample_timestamps(timestamps: np.ndarray, initial_Hz: float, desired_Hz: float) -> np.ndarray:
    if desired_Hz < initial_Hz:
        raise ValueError("Downsampling is not supported.")
    
    t_orig = np.arange(timestamps.shape[0]) / initial_Hz
    t_new = np.arange(t_orig[0], t_orig[-1] + 1/desired_Hz, 1/desired_Hz)
    
    upsampled_timestamps = np.interp(t_new, t_orig, timestamps)
    return upsampled_timestamps

# This function was written by ChatGPT
def linear_interpolate(time_original: np.ndarray, data_original: np.ndarray, original_frequency: float, target_frequency: float) -> tuple[np.ndarray, np.ndarray]:
    if len(time_original) != len(data_original):
        raise ValueError("Time and data arrays must have the same length.")
    if original_frequency <= 0 or target_frequency <= 0:
        raise ValueError("Frequencies must be positive values.")

    # Calculate the time interval for the target sampling rate
    dt_target = 1 / target_frequency

    # Determine the start and end time of the original data
    start_time = time_original[0]
    end_time = time_original[-1]

    # Generate the time points for the target sampling rate
    time_target = np.arange(start_time, end_time + dt_target, dt_target)
    # Handle edge case
    if time_target[-1] > end_time:
        time_target = time_target[:-1]
        
    data_target = []
    original_index = 0

    for target_time in time_target:
        # Find the two original time points that surround the target time
        while original_index < len(time_original) - 1 and time_original[original_index + 1] < target_time:
            original_index += 1

        # Perform linear interpolation
        if original_index < len(time_original) - 1:
            t1 = time_original[original_index]
            t2 = time_original[original_index + 1]
            y1 = data_original[original_index]
            y2 = data_original[original_index + 1]
            interpolated_value = y1 + (y2 - y1) * (target_time - t1) / (t2 - t1)

        # Handle the case where target_time is before the first original time
        elif original_index == 0 and target_time < time_original[0]:
            interpolated_value = data_original[0]
        # Handle the case where target_time is after the last original time
        else:
            interpolated_value = data_original[-1]

        data_target.append(interpolated_value)

    return time_target, np.array(data_target)