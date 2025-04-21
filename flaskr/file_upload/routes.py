# written by brian, with inspiration from matt's original design (the variable-checking)
# in the midst of a rewrite for more robust handling of files in general

# base
import uuid

# flask
from flask import render_template, flash, request, redirect, jsonify
from flask_login import current_user

# local
from flaskr.file_upload import blueprint
from flaskr.file_upload.forms import *
from flaskr.file_upload.methods import *

# create uploads directory if it doesn't already exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@blueprint.before_request
def setup():
    # Only generate a new UUID if it's not already in the session
    if 'upload_uuid' not in session:
        session['upload_uuid'] = str(uuid.uuid4())
    
    # create the submitted flags
    if 'data_submitted' not in session:
        session['data_submitted'] = False
    if 'videos_submitted' not in session:
        session['videos_submitted'] = False
        
    # designate an uuid-upload folder, creating it if it doesn't exist
    request.upload_path = os.path.join(UPLOAD_FOLDER, session['upload_uuid'])
    if not os.path.exists(request.upload_path):
        remove_empty_dirs(UPLOAD_FOLDER)
        os.makedirs(request.upload_path, exist_ok=True)

@blueprint.route("/file_upload", methods=["GET", "POST"])
def file_upload():
    if not current_user.is_authenticated:
        return redirect("/")

    # url forms and buttons
    databraryurl = DatabraryURLForm()
    osfurl = OSFURLForm()
    visualizer_button = EnterVisualizer()
    reset_button = ResetFileUpload()

    # If submitting via URL download
    if databraryurl.validate_on_submit() and databraryurl.dtb_submit.data:
        dtb_extraction_path = fetch_and_unzip(download_databrary_videos, databraryurl.dtb_url.data, request.upload_path)

        if "Error" in dtb_extraction_path:
            flash(f"Error processing Databrary files: {dtb_extraction_path}", 'error')
        else:
            if files_exist(request.upload_path, ['.mp4', '.csv']):
                flash(f"Videos from Databrary stored in: {dtb_extraction_path}")
                session['videos_submitted'] = True
            else:
                flash("No files were uploaded for Databrary.", 'error')

    if osfurl.validate_on_submit() and osfurl.osf_submit.data:
        osf_extraction_path = fetch_and_unzip(download_osf_data, osfurl.osf_url.data, request.upload_path)

        if "Error" in osf_extraction_path:
            flash(f"Error processing OSF files: {osf_extraction_path}", 'error')
        else:
            if files_exist(request.upload_path, ['.pldata', '.npy', '.npz', '.yaml', '.intrinsics', '.extrinsics']):
                session['data_submitted'] = True
            else:
                flash("No files were uploaded for OSF.", 'error')

    # Handle visualizer button
    if visualizer_button.validate_on_submit() and visualizer_button.submit.data:
        # check if certain files are in the directory
        required_files = ['odometry.pldata', 'gaze.npz']
        missing_files = [f for f in required_files if not os.path.isfile(os.path.join(request.upload_path, f))]

        if missing_files:
            flash(f"The following required files are missing: {', '.join(missing_files)}", 'danger')
        else:
            try:
                # Normalize video filenames and add session to database
                print('success! will add to db and redirect to visualizer')
                normalize_video_filenames(request.upload_path)
                add_session_to_db(session['upload_uuid'])

                # Pop session variables
                session.pop('data_submitted', None)
                session.pop('videos_submitted', None)

                # Redirect to the visualizer
                return redirect("/visualizer")
            except KeyError:
                flash("Session data is missing or invalid.", 'danger')
            except Exception as e:
                flash(f"An error occurred: {str(e)}", 'danger')

    # Handle reset button
    if reset_button.validate_on_submit() and reset_button.reset.data:
        clear_directory(request.upload_path)
        session.pop('data_submitted', None)
        session.pop('videos_submitted', None)


    return render_template("file_upload/file_upload.html",
                           is_admin=is_admin(),
                           data_submitted=session.get('data_submitted'),
                           videos_submitted=session.get('videos_submitted'),
                           databraryurl=databraryurl,
                           osfurl=osfurl,
                           visualizer_button=visualizer_button,
                           reset_button=reset_button
                           )

@blueprint.route('/upload', methods=['POST'])
def upload_file():
    if 'filepond' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['filepond']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the file to the user's uuid upload folder
    save_path = os.path.join(request.upload_path, file.filename)
    file.save(save_path)
    
    # Set session flags based on file type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext in ['.mp4', '.csv']:
        session['videos_submitted'] = True
        print(f"Data Submitted: {session.get('data_submitted')}")
    
    if ext in ['.pldata', '.npy', '.npz', '.yaml', '.intrinsics', '.extrinsics']:
        session['data_submitted'] = True
        print(f"Data Submitted: {session.get('data_submitted')}")
    
    # Return the response to FilePond
    return jsonify({'id': file.filename})
