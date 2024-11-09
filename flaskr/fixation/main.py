from fixation_packages.ingestion import extract_unzip, read_pldata, parse_pldata
from fixation_packages import gaze_processing
from fixation_packages.IMU_processing import calculate_optic_flow_vec


import numpy as np
import pandas as pd
import msgpack
import collections
import requests
import zipfile
from io import BytesIO
import os
from pathlib import Path

from constants import *       # import all global constants as defined in constants.py


def main():
    # extract_unzip(DOWNLOAD_URL)

    data_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'test', DATE_OF_URL_DATA))

    print("GUH!")
    time_array = np.load(f'{data_path}/{NPY_TO_LOAD}')
    time_series = pd.to_datetime(time_array, unit='s')
    # print(time_series)

    pldata_data = read_pldata(f'{data_path}/{PLDATA_TO_LOAD}')

    df = pd.DataFrame(pldata_data)
    parsed_data = parse_pldata(df[1].iloc[0])
    list_all = []
    for i in range(len(df)):
        # list_all.append(parse_pldata(df[1].iloc[i]))
        print(parse_pldata(df[1].iloc[i]))

    # print(parsed_data)

    # for i in range(len(list_all)-1):
    #     calculate_optic_flow_vec(list_all[i], list_all[i+1])

main()