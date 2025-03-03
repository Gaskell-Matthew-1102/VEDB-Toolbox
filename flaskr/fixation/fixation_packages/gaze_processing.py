# All code in this file is our own work.

# Module to process the gaze data stream
# First, low pass filter using Savitzky-Golay filter with 55ms window length and 3rd grade polynomial
# Steps 1, 2
import numpy as np
from scipy.signal import savgol_filter
from constants import GAZE_WINDOW_SIZE_MS, POLYNOMIAL_GRADE

# WINDOW_SIZE_MS = 55
# POLYNOMIAL_GRADE = 3

# Wrapper function for Savitzky-Golay filter with specified parameters set as default arguments
def savgol(input, window_length=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE) -> np.array:
    output = savgol_filter(input, window_length, polynomial_grade)
    return output

# Returns a np.array of calculated gaze velocities in pixels/sec from the filtered gaze data
def calculateGazeVelocity(input:np.array) -> np.array:
    # workingList = np.array([])
    # for i in range(len(input) - 1):
    #     print(i)
    #     workingList = np.append(workingList, input[i+1] - input[i])
    # a = np.diff(input)
    return np.diff(input)
