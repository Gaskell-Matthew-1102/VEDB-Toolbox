#accountManagement
from flask_login import login_user, logout_user, current_user
from .models import db, Users
from .file_upload import *
from werkzeug.security import generate_password_hash, check_password_hash

def uploadUser(uploadedData):   #Uploading a single user
    if uploadedData[3] == "on":
        user = Users(username=uploadedData[0], email=uploadedData[1], password=generate_password_hash(uploadedData[2]), administrator=True)
    else:
        user = Users(username=uploadedData[0], email=uploadedData[1],password=generate_password_hash(uploadedData[2]), administrator = False)

    # write to DB
    db.session.add(user)
    db.session.commit()
    flash("Registration successful! Welcome.", "success")

def uploadCSV():    #Uploading users in mass through a CSV file.
    print("hi")