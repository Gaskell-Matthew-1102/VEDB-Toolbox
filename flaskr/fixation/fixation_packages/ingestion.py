import numpy as np
import pandas as pd
import msgpack
import collections
import requests
import zipfile
from io import BytesIO
import os
from pathlib import Path

# TEMP CONSTANT GLOBALS
# DOWNLOAD_URL = "https://osf.io/85usz/download"
# DATE_OF_URL_DATA = "2023_06_01_18_47_34"
# NPY_TO_LOAD = "gyro_timestamps.npy"
# PLDATA_TO_LOAD = "accel.pldata"


# WORLD CAMERA (FLIR Chameleon 3): 30fps
# HEAD TRACKING MODULE (RealSense T265): 30fps
# EYE TRACKING (Pupil Labs Pupil-Core): 120fps



def read_pldata(file_path):
    with open(file_path, 'rb') as file:
        unpacker = msgpack.Unpacker(file, raw=False)
        data = []
        for packet in unpacker:
            data.append(packet)
    return data

def parse_pldata(data):
    unpacker = msgpack.Unpacker(BytesIO(data), raw=False)
    parsed_data = next(unpacker)
    
    #flatten nested structures
    flattened = {}
    for key, value in parsed_data.items():
        if isinstance(value, list):
            for i, item in enumerate(value):
                flattened[f"{key}_{i}"] = item
        else:
            flattened[key] = value
    
    return flattened

def extract_unzip(file):
    zip_url = file
    response = requests.get(zip_url)
    if response.status_code == 200:
        print("Download successful")
    else:
        raise Exception(f"Failed to download file: {response.status_code}")
    zip_file = zipfile.ZipFile(BytesIO(response.content)) # get the zip file
    filepath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'test'))
    zip_file.extractall(filepath)

def main():
    pass
    # extract_unzip(DOWNLOAD_URL)

    # data_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'test', DATE_OF_URL_DATA))

    # print("GUH!")
    # time_array = np.load(f'{data_path}/{NPY_TO_LOAD}')
    # time_series = pd.to_datetime(time_array, unit='s')
    # print(time_series)

    # odometry_data = read_pldata(f'{data_path}/{PLDATA_TO_LOAD}')

    # df = pd.DataFrame(odometry_data)
    # parsed_data = parse_pldata(df[1].iloc[0])
    # list_all = []
    # for i in range(len(df)):
    #     list_all.append(parse_pldata(df[1].iloc[i]))
    # print(parsed_data)
    # print('\n\n')
    # print(parsed_data['linear_acceleration_0'] - parse_pldata(pd.DataFrame(read_pldata(f'{data_path}/{'odometry.pldata'}'))[1].iloc[0])['linear_acceleration_0'])