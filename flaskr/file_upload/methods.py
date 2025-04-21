# validate link, download funcs are matt's work with some modification
# fetch_&_unzip is a rewrite by brian for more "generalized" handling
# overall brian

# base
import os
import re
import zipfile
from io import BytesIO
import shutil

# flask
from flask import session, redirect
from flask_login import current_user

# pip
import requests
from urllib.request import Request, urlopen

from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

# local
from flaskr import db
from flaskr.models import User, SessionHistory

# Recursively removes empty (checks) UUID-directories in the given root directory.
def remove_empty_dirs(base_dir):
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for name in dirs:
            dir_path = os.path.join(root, name)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f"Deleted empty directory: {dir_path}")

# returns the admin bool (T/F) from the table
def is_admin():
    return User.query.filter_by(username=current_user.username).first().admin

# Helper function to download video files from a Databrary URL
# NOTE!! UNTESTED!! DATABRARY IS NOT KIND
def download_databrary_videos(link: str) -> bytes:
    headers = {
        'Accept': 'text/html, */*; q=0.01, gzip, deflate, br, zstd, en-US, en; q=0.9',
        'Referer': 'https://databrary.org/volume/1612/slot/65955/zip/false',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    }
    return urlopen(Request(link, headers=headers)).read()

# Helper function to download data files from OSF
def download_osf_data(link: str) -> bytes:
    response = requests.get(link)
    if response.status_code != 200:
        raise Exception(f"Failed to download file: {response.status_code}")
    return response.content

# Helper function to unzip content into a specified directory without creating a new subdir
def fetch_and_unzip(download_func, url_string: str, unzip_to: str) -> str:
    try:
        if url_string.startswith("https"):
            response = download_func(url_string)
            zip_data = BytesIO(response)
        else:
            zip_data = open(url_string, 'rb')

        with zipfile.ZipFile(zip_data) as zip_file:
            # Get all file paths in the zip
            all_paths = zip_file.namelist()

            # Detect the common top-level directory (if any)
            top_dirs = set(p.split('/')[0] for p in all_paths if '/' in p and not p.startswith('__MACOSX'))
            common_prefix = top_dirs.pop() if len(top_dirs) == 1 else ''

            for member in zip_file.infolist():
                original_path = member.filename

                # Skip directories
                if member.is_dir():
                    continue

                # If the file is inside 'processedgaze', adjust the path
                if 'processedGaze' in original_path:
                    # Remove 'processedgaze' prefix from the path
                    relative_path = original_path.replace('processedGaze' + '/', '')
                elif common_prefix and original_path.startswith(common_prefix + '/'):
                    # Remove the common top-level directory
                    relative_path = original_path[len(common_prefix)+1:]
                else:
                    # Use the original path if no specific folder is found
                    relative_path = original_path

                # Construct the final output path
                target_path = os.path.join(unzip_to, relative_path)

                # Ensure parent dirs exist
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # Write the file
                with zip_file.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())

        return unzip_to

    except Exception as e:
        return str(e)

def files_exist(upload_path, allowed_extensions=None):
    for f in os.listdir(upload_path):
        if os.path.isfile(os.path.join(upload_path, f)):
            if allowed_extensions is None or f.lower().endswith(tuple(allowed_extensions)):
                return True
    return False

# delete files in a given path
def clear_directory(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        os.makedirs(path)

# Add new session to database (after successful dual upload)
def add_session_to_db(uuidfolder: str):
    user = User.query.filter_by(username=current_user.username).first()
    
    try:
        new_session = SessionHistory (
            session_id = uuidfolder,  # created folder. will have files in it and thus will not be deleted during create_user_directory()
            user_id = user.id
        )
        db.session.add(new_session)
        db.session.commit()
        return {"status": "success", "message": "Session successfully added to DB."}
    except SQLAlchemyError as e:
        # Handle database-related errors
        db.session.rollback()
        return {"status": "error", "message": "An error occurred while interacting with the database."}

    except Exception as e:
        # Handle other errors
        return {"status": "error", "message": "An unexpected error occurred."}

# renames eye0*.mp4 to eye0.mp4, and so forth
def normalize_video_filenames(upload_path):
    filename_map = {
        'eye0': re.compile(r'^eye0.*\.mp4$', re.IGNORECASE),
        'eye1': re.compile(r'^eye1.*\.mp4$', re.IGNORECASE),
        'world': re.compile(r'^world.*\.mp4$', re.IGNORECASE),
    }

    for target_name, pattern in filename_map.items():
        for filename in os.listdir(upload_path):
            if pattern.match(filename):
                source_path = os.path.join(upload_path, filename)
                target_path = os.path.join(upload_path, f"{target_name}.mp4")

                # If the file is already normalized, skip
                if source_path == target_path:
                    continue

                # Remove existing target to prevent rename error
                if os.path.exists(target_path):
                    os.remove(target_path)

                os.rename(source_path, target_path)
                break  # Stop after renaming the first match