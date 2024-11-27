import requests
from io import BytesIO
import zipfile
import os

# Downloads files from a given link
def download_from_url(link: str):
    response = requests.get(link)

    if response.status_code != 200:
        print(f"FAILED TO DOWNLOAD DATA FROM URL. STATUS CODE: {response.status_code}")
        raise Exception(f"Failed to download file: {response.status_code}")
    return response

# Downloads video files when presented with a Databrary link. The logic for downloading a file from this site is a little different, so a new function :)
def download_video_files(link: str) -> requests.Response:
    session = requests.Session()
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        # 'cookie': 'cf_clearance=WRiqWdK.GPHYJftBXKmzXgkJGQKmNYxHLXG.Fir.k.E-1732657382-1.2.1.1-n_QjzeWHvDnWuTRY1ktsfiXF3GrPzF.vT30gOEA1yABgBkzV5mWvDa4pAGZgHwstiUlx16qj6i6e3dJTzVBbhzF0heUGxKNch2pP3X.ib08f0ZkF4RBble2.NcvcTbaYir.Jz1CwphVwXjjTK94FDPaKIQgW2JzlIQwkcRo9XhBCrtYrhXLaGKMCCoy3HUbt3Sg936ushfQQGayilj_pfHhx4y.0DHypQgF6zsbzxsQd9ZbCnyOmwg0zN2CDy0lMZrrH3tkdrnK.ODZTvak9QdESfyVhVRV9BO3nYcY55zDYtc3tdCxtwlpHcgLDbWU0XN2P_ovDZ6ohrvXQNzuX8Nav4nNyikxsh4BsDLo9KLm.xwF6qm02q1UPNEakv4Cu',
        'dnt': '1',
        'priority': 'u=0, i',
        'referer': 'https://nyu.databrary.org/volume/1612/slot/65955/zip/false',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    response = session.get(link, headers=headers)

    print(session.cookies.items())
    print()
    for key in response.headers:
        print(key)

    # print(f"Cookies: {response.headers}")

    if response.status_code == 200:
        print("Authenticated successfully!")
    else:
        print(f"Authentication failed with status code: {response.status_code}")
        print(response.text)  # Print the error message
    return response

def download_files(link: str):
    response = requests.get('https://nyu.databrary.org/volume/1612/slot/65955/zip/false')
    if(response.status_code != 200):
        print(f"FAILED TO DOWNLOAD VIDEO FROM URL. STATUS CODE: {response.status_code}")
    return response

# The original code for this function was given to us by Brian Szekely, a PhD student and former student of
# Dr. MacNeilage's Self-Motion Lab. It has been slightly altered to fit our code.
# This function takes in a respinse from a GET response and unzips it
def extract_unzip(response: requests.Response) -> bool:
    print(f"Response status code: {response.status_code}")
    # print(f"Response content: {response.content}")
    zip_file = zipfile.ZipFile(BytesIO(response.content)) # get the zip file
    print("AAA")
    filepath = os.path.abspath(os.path.dirname( __file__ ))
    zip_file.extractall(filepath)
    return True




vid_link = "https://nyu.databrary.org/volume/1612/slot/65955/zip/false"

response = download_video_files(vid_link)
print(f"AAAAAA: {response.status_code}")
extract_unzip(response)