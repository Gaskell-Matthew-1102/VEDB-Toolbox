# ingestion (0)
DOWNLOAD_URL = "https://osf.io/85usz/download"
DATE_OF_URL_DATA = "2023_06_01_18_47_34"
NPY_TO_LOAD = "odometry_timestamps.npy"
PLDATA_TO_LOAD = "odometry.pldata"

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