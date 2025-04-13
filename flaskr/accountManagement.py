#accountManagement
ALLOWED_EXTENSIONS = {'csv'}
from .models import db, Users
from .file_upload import *
from werkzeug.security import generate_password_hash
import csv

def uploadUser(uploadedData):   #Uploading a single user
    if uploadedData[3] == "on" or uploadedData[3] == "true":
        user = Users(username=uploadedData[0], email=uploadedData[1], password=generate_password_hash(uploadedData[2]), administrator=True)
    else:
        user = Users(username=uploadedData[0], email=uploadedData[1],password=generate_password_hash(uploadedData[2]), administrator = False)

    # write to DB
    db.session.add(user)
    db.session.commit()
    flash("Registration successful! Welcome.", "success")

def verifyCSV(validatingFile):    #Uploading users in mass through a CSV file.
    #check if its even a file
    if not '.' in validatingFile:
        return False
    #check if its a csv file
    if not validatingFile.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        return False
    #check if no more than 3 items per row
    with open(validatingFile, newline='') as csvfile:
        csvlist = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvlist:
            if not len(row) == 4:
                return False
    return True
