# Constants file for use in the module. Our own work.

# ingestion (0)
DOWNLOAD_URL = "https://osf.io/85usz/download"
DATE_OF_URL_DATA = "2021_03_16_17_18_42"       # "2023_06_01_18_47_34" was original
NPY_TO_LOAD = "odometry_timestamps.npy"
PLDATA_TO_LOAD = "odometry.pldata"
NPZ_TO_LOAD = "gaze.npz"

# gaze processing (1, 2)
GAZE_WINDOW_SIZE_MS = 55            # milliseconds
POLYNOMIAL_GRADE = 3

# adaptive threshold (5, 6, 7)
MIN_VEL_THRESH = 750                # pixels/sec
GAIN_FACTOR = 0.8
ADAP_WINDOW_SIZE_MS = 300           # milliseconds

# filters (9, 10)
MIN_SACCADE_AMP = 1.0               # degrees
MIN_SACCADE_DUR_MS = 10             # milliseconds
MIN_FIXATION_DUR_MS = 70            # milliseconds
HFOV_DEG = 70                       # THIS VALUE IS COMPLETELY AND UTTERLY MADE UP

# Vectors are represented in this project as a 2 by X np.ndarray, where X is the number of components in the vector
#                       
# Example: the vector: <1, 2, 3> is represented as [[1, 2, 3]]
# 
# 
# 
# 
# 
# 
