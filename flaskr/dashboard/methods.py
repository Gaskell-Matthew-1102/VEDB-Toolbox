# written by leon, organized by brian
# converted some of the routes' logic to methods
# admin_required by brian

# base
import csv
from functools import wraps

# flask
from flask import flash, render_template, redirect
from flask_login import current_user

# pip
from werkzeug.security import generate_password_hash

# local
from flaskr import db
from flaskr.models import User, SessionHistory

ALLOWED_EXTENSIONS = {'csv'}

# created @admin_required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'admin', False):
            return redirect("/file_upload")
        return f(*args, **kwargs)
    return decorated_function

# simplification of routes.py
def render_dashboard(search_filter, search_type, warning, **kwargs):
    result_list = searchbar(search_filter, search_type)
    sessions = load_session_data(result_list)
    return render_template('dashboard/dashboard.html', userlist=result_list, warning=warning, sessionlist=sessions, **kwargs)

### used to be accountManagement.py
def upload_user(uploaded_data):  #Uploading a single user
    if uploaded_data[3] == "on" or uploaded_data[3] == "true":
        user = User(username=uploaded_data[0], email=uploaded_data[1], password_hash=generate_password_hash(uploaded_data[2]), admin=True)
    else:
        user = User(username=uploaded_data[0], email=uploaded_data[1], password_hash=generate_password_hash(uploaded_data[2]), admin=False)
    
    # write to DB
    db.session.add(user)
    db.session.commit()
    flash("Registration successful! Welcome.", "success")


def verify_csv(validating_file):
    if '.' not in validating_file:
        return False

    ext = validating_file.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False

    try:
        with open(validating_file, newline='') as csvfile:
            csvlist = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in csvlist:
                if len(row) != 4:
                    return False
    except Exception as e:
        print(f"CSV validation error: {e}")
        return False

    return True

### search.py
def searchbar(search_filter, search_type):
    result_list = []
    if search_filter == "":
        result_list = User.query.with_entities(User.id, User.username, User.email, User.admin).all()
    elif search_type == "email":  #Search by Email
        emaiList = email_match(search_filter)
        for user in emaiList:
            foundUser = User.query.with_entities(User.id, User.username, User.email, User.admin).filter_by(
                email=user).all()
            for a in foundUser:
                result_list.append(a)
    elif search_type == "username":  #Search by username
        userList = user_match(search_filter)
        for user in userList:
            foundUser = User.query.with_entities(User.id, User.username, User.email, User.admin).filter_by(
                username=user).all()
            for a in foundUser:
                result_list.append(a)
    return result_list


def user_match(key):
    listOfUsers = [username for (username,) in User.query.with_entities(User.username).all()]
    return [u for u in listOfUsers if key in u]

def email_match(key):
    listOfEmails = [email for (email,) in User.query.with_entities(User.email).all()]
    return [e for e in listOfEmails if key in e]

def session_match(key):
    listOfUIDS = []
    allses = SessionHistory.query.with_entities(SessionHistory.user_id, SessionHistory.session_name).all()
    for ses in allses:
        if key in ses[1]:
            listOfUIDS.append(ses[0])
    return listOfUIDS

def load_session_data(userList):
    session_list = []

    for row in userList:
        single_session = SessionHistory.query.with_entities(SessionHistory.session_id , SessionHistory.user_id ,SessionHistory.session_name).filter_by(user_id=row[0]).all()
        for a in single_session:
            session_list.append(a)

    return session_list

def findsession(searchTerm):
    # Similar to the other searches, empties should just reset the search
    username_list = []
    if searchTerm == "":
        result_list = User.query.with_entities(User.id, User.username, User.email, User.admin).all()
        return result_list
    # Otherwise, search through session names
    else:
        # Search sessions by session name, and return list of the associated UIDs
        all_sessions_uid = session_match(searchTerm)
        # Use UIDs to get user information
        for uid in all_sessions_uid:
            foundUser = User.query.with_entities(User.id, User.username, User.email, User.admin).filter_by(id=uid).all()
            for element in foundUser:
                username_list.append(element)
        # Return the list of user data
        return username_list
