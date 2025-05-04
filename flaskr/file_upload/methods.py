# validate link, download funcs are matt's work with some modification
# fetch_&_unzip is a rewrite by brian for more "generalized" handling

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

# file/folder manipulation
# Recursively removes UUID-directories not accounted for in the session history table. this avoids leaving unused non-empty directories
def remove_unaccounted_dirs(base_dir):
    # Fetch all session_ids from the session_history table
    session_ids = {session_entry.session_id for session_entry in SessionHistory.query.all()}

    # Folders to exclude from deletion
    protected_dirs = {"export"}

    # Walk through the directory
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for name in dirs:
            if name in protected_dirs:
                continue  # Skip protected folders

            dir_path = os.path.join(root, name)

            # Check if the directory's name (UUID) is not in session_history
            if name not in session_ids:
                # Remove the unaccounted directory
                shutil.rmtree(dir_path)
                print(f"Deleted unaccounted directory: {dir_path}")

# checks if files exist in upload_path, particularly with an array of allowed extensions
def files_exist(upload_path, allowed_extensions=None):
    for f in os.listdir(upload_path):
        if os.path.isfile(os.path.join(upload_path, f)):
            if allowed_extensions is None or f.lower().endswith(tuple(allowed_extensions)):
                return True
    return False

# renames *eye0*.mp4 to eye0.mp4, and so forth to make it easier for us to use
def normalize_video_filenames(upload_path):
    filename_map = {
        'eye0': re.compile(r'^.*eye0.*\.mp4$', re.IGNORECASE),
        'eye1': re.compile(r'^.*eye1.*\.mp4$', re.IGNORECASE),
        'world': re.compile(r'^.*world.*\.mp4$', re.IGNORECASE),
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

# grabs name of csv (likely datetime of session) and returns it for use in SessionHistory
def get_csv_filename(upload_path):
    for filename in os.listdir(upload_path):
        if filename.lower().endswith('.csv') and os.path.isfile(os.path.join(upload_path, filename)):
            # Remove the .csv extension, so its just the datetime
            return os.path.splitext(filename)[0]
    return None  # or raise an error if you expect one to always be there

# URL-downloading functions
# UNTESTED!!! helper function to download video files from a Databrary URL
def download_databrary_videos(link: str) -> bytes:
    headers = {
        'Accept': 'text/html, */*; q=0.01, gzip, deflate, br, zstd, en-US, en; q=0.9',
        'Referer': 'https://databrary.org/volume/1612/slot/65955/zip/false',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    }
    return urlopen(Request(link, headers=headers)).read()

# Helper function to download data files from an OSF URL
def download_osf_data(link: str) -> bytes:
    response = requests.get(link)
    if response.status_code != 200:
        raise Exception(f"Failed to download file: {response.status_code}")
    return response.content

# "General" function to fetch data and unzip it in a specified directory and returns that as a string
def fetch_and_unzip(download_func, url_string: str, unzip_to: str) -> str:
    try:
        if url_string.startswith("https"):
            response = download_func(url_string)
            zip_data = BytesIO(response)
        else:
            zip_data = open(url_string, 'rb')

        with zipfile.ZipFile(zip_data) as zip_file:
            for member in zip_file.infolist():
                # Skip directories
                if member.is_dir():
                    continue

                # Extract only the filename (ignore folder paths)
                filename = os.path.basename(member.filename)
                if not filename:
                    continue  # skip if it's an empty filename

                # Create the full output path
                target_path = os.path.join(unzip_to, filename)

                # Ensure the target directory exists
                os.makedirs(unzip_to, exist_ok=True)

                # Write the file to the flattened directory
                with zip_file.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())

        return unzip_to

    except Exception as e:
        return str(e)

# Database querying
# returns the admin bool (T/F) from the table
def is_admin():
    return User.query.filter_by(username=current_user.username).first().admin

# Add new session to database (after successful dual upload)
def add_session_to_db(uuidfolder: str, sesh_name: str):
    user = User.query.filter_by(username=current_user.username).first()
    
    try:
        new_session = SessionHistory (
            session_id = uuidfolder,  # created folder. will have files in it and thus will not be deleted during create_user_directory()
            user_id = user.id,
            session_name = sesh_name
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
