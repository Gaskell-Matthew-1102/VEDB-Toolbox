# All code in this file is our own work.

# Module to process the gaze data stream
# First, low pass filter using Savitzky-Golay filter with 55ms window length and 3rd grade polynomial
# Steps 1, 2

from scipy.signal import savgol_filter
from constants import GAZE_WINDOW_SIZE_MS, POLYNOMIAL_GRADE

# WINDOW_SIZE_MS = 55
# POLYNOMIAL_GRADE = 3

# Wrapper function for Savitzky-Golay filter with specified parameters set as default arguments
def savgol(input, window_length=GAZE_WINDOW_SIZE_MS, polynomial_grade=POLYNOMIAL_GRADE):
    output = savgol_filter(input, window_length, polynomial_grade)
    return output

# Returns a list??? of calculated gaze velocities in pixels/sec from the filtered gaze data
def calculateGazeVelocity(input):
    workingList = []
    for i in range(len(input) - 1):
        workingList.append(input[i+1] - input[i])
    return workingList



# import numpy as np
# import matplotlib.pyplot as plt

# np.random.seed(0)
# x = np.linspace(0, 2 * np.pi, 100)
# y = np.sin(x) + np.random.normal(0, 0.1, x.size)

# y_smooth = savgol(y)
# calculateGazeVelocity(y)

# plt.plot(x, y, label='Noisy Signal')
# plt.plot(x, y_smooth, label='Smoothed Signal', color='red')
# plt.grid(lw=2,ls=':')
# plt.xlabel('Time Step')
# plt.ylabel("Value")
# plt.legend()
# plt.show()