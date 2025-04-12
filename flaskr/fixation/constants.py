# Constants file for use in the module. Our own work.

# ingestion (0)
DOWNLOAD_URL = "https://osf.io/85usz/download"
DATE_OF_URL_DATA = "2023_06_01_18_47_34"       # "2023_06_01_18_47_34" was original
NPY_TO_LOAD = "odometry_timestamps.npy"
PLDATA_TO_LOAD = "odometry.pldata"
NPZ_TO_LOAD = "gaze.npz"

# gaze processing (1, 2)
GAZE_WINDOW_SIZE_MS = 55            # milliseconds
POLYNOMIAL_GRADE = 3

# adaptive threshold (5, 6, 7)
MIN_VEL_THRESH = 700                # pixels/sec      OLD WAS 750, 700 for fallback
GAIN_FACTOR = 0.8
ADAP_WINDOW_SIZE_MS = 200           # milliseconds      200ms for fallback option

# filters (9, 10)
MIN_SACCADE_AMP_DEG = 1.0           # degrees
MIN_SACCADE_DUR_MS = 10             # milliseconds
MIN_FIXATION_DUR_MS = 70            # milliseconds
HFOV_DEG = 110                      # degrees, FOV of lens

X_RES = 400         # originally 192x192
Y_RES = 400
# Vectors are represented in this project as a 2 by X np.ndarray, where X is the number of components in the vector
#                       
# Example: the vector: <1, 2, 3> is represented as [[1, 2, 3]]
# The list of vectors of <1, 2> and <3, 4> should be represented as [[1, 2], [3, 4]]
# 
# 
# 
# 
# 
