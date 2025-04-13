"""
1st version of this file was based on a DigitalOcean tutorial that has
since been rewritten constantly to suit our needs. at this point this is
100% our (Brian, Leon) work
"""

# auth.py
from flask_login import login_user, logout_user, current_user
from .file_upload import *
from .forms import LoginForm, RegistrationForm
from .search import searchBar
from .accountManagement import *
import csv
import os
from werkzeug.utils import secure_filename
from flask import current_app

# Home route
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('landing'))
    form1 = get_showform(1)
    form2 = get_showform(2)
    return render_template("file-upload/file_upload.html", show_form1=form1, show_form2=form2, isAdmin=current_user.administrator)

# Landing route
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from flaskr.models import db, Users
from flaskr.forms import LoginForm, RegistrationForm

def landing():
    login_form = LoginForm()
    signup_form = RegistrationForm()

    if signup_form.validate_on_submit():
        # Check if user already exists
        if (Users.query.filter_by(username=signup_form.username.data).first()) or (signup_form.password.data != signup_form.repeat_password.data):
            # Check which condition triggered the flash message
            if Users.query.filter_by(username=signup_form.username.data).first():
                flash("Username already in use!", "danger")
            else:
                flash("Passwords not matching!", "danger")

            # Clear the password and repeat_password fields
            signup_form.password.data = ''
            signup_form.repeat_password.data = ''
            # Return to the landing page with the existing form values
            return render_template("home/home.html", login_form=login_form, signup_form=signup_form)

        # Create user
        user = Users(username=signup_form.username.data, email=signup_form.email.data, password=generate_password_hash(signup_form.password.data))

        # Write to DB
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Welcome.", "success")
        
        # Log in user after creation
        login_user(user)
        return redirect(url_for("home"))

    if login_form.validate_on_submit():
        user = Users.query.filter_by(username=login_form.username.data).first()

        if user and check_password_hash(user.password, login_form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username/password!", "danger")

    # Render the template with the form, including values for pre-filling
    return render_template("home/home.html", login_form=login_form, signup_form=signup_form)

    
# Logout route
def logout():
    show_form1 = get_showform(1)
    show_form2 = get_showform(2)
    if not show_form1:
        video_files = get_video_list()
        delete_files_in_list(video_files)
    if not show_form2:
        data_files = get_data_file_list()
        delete_files_in_list(data_files)
    if not show_form1 and not show_form2:
        graph_files = get_graph_file_list()
        delete_files_in_list(graph_files)
    clear_lists()
    logout_user()
    return redirect(url_for("home"))

def team():
    return render_template("home/team.html")

def faculty():
    return render_template("home/faculty.html")

# Dashboard Route
def dashboard():
    user = Users.query.filter_by(username=current_user.username).first()
    if user.administrator:
        userlist = searchBar("", "reset")
        return render_template('user-tools/strappedDash.html', userlist=userlist, warning=0)
    else:
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2, isAdmin=False)

def searchuser():
    if request.form["formType"] == "email":   #Search through email bar
        emaillist = searchBar(request.form.get('email_search', ""), "email")
        return render_template('user-tools/strappedDash.html', userlist=emaillist, warning=0)
    elif request.form["formType"] == "username":  #search through username bar
        userlist = searchBar(request.form.get('user_search', ""), "username")
        return render_template('user-tools/strappedDash.html', userlist=userlist, warning=0)
    else:   #reset search
        userlist = searchBar("", "reset")
        return render_template('user-tools/strappedDash.html', userlist=userlist, warning=0)

def adduser():
    # check if user already exists
    if Users.query.filter_by(username=request.form.get('unEnter', "")).first():
        flash("Username already in use!", "danger")
        userlist = searchBar("", "reset")
        return render_template('user-tools/strappedDash.html', userlist=userlist, warning=1)
    else:
        uploadedUserData = [request.form.get('unEnter', ""), request.form.get('emEnter', ""), request.form.get('pwEnter', ""), request.form.get('admEnter', ""), request.form.get('admEnter', "")]
        #print(request.form.get('admEnter', ""))
        uploadUser(uploadedUserData)
        userlist = searchBar("", "reset")
        return render_template('user-tools/strappedDash.html', userlist=userlist, warning=2)

def deleteuser():
    deleting = request.form.get('user_to_delete', "")
    foundUser = Users.query.with_entities(Users.id).filter_by(username=deleting).all()

    #As of now, foundUser is a list with a list with the id
    for a in foundUser:
        for b in a:
            #refuses to delete account if the account being deleted is the one using to delete
            #basically, you cannot delete yourself
            if b == current_user.id:
                userlist = searchBar(request.form.get('user_search', ""), "username")
                return render_template('user-tools/strappedDash.html', userlist=userlist, warning=4)
            #otherwise, continue through with deletion
            else:
                Users.query.filter_by(id=b).delete()
                db.session.commit()

    userlist = searchBar(request.form.get('user_search', ""), "username")
    return render_template('user-tools/strappedDash.html', userlist=userlist, warning=3)

def csvupload():
    rejectFlag = 2
    rejectCount = 0
    userCount = 0
    #thanks matt
    #THIS, is a CRAFTING TABLE. (save the file)
    if request.method == 'POST':
        file_link = request.files['filename']
        file_link.save(file_link.filename)
        name =  file_link.filename

    #first, we MINE! (let's verify the file itself before we parse it)
        if not verifyCSV(name): #if not the correct file,
            os.remove(name) #remove incorrect file
            userlist = searchBar("", "reset")
            return render_template('user-tools/strappedDash.html', userlist=userlist, warning=1)

        os.rename(name, "flaskr/static/userupload.csv")

    #then we CRAFT! (parse the csv file data)
        with open("flaskr/static/userupload.csv", newline='') as csvfile:
            listOfUsers = csv.reader(csvfile, delimiter=',', quotechar='|')

    #flint and STEEL! (we check to see if the data itself is valid, specifically the username)
            for row in listOfUsers:
                userCount += 1
                if Users.query.filter_by(username=row[0]).first():  #reject if list has an existing user already
                    print("no it is now ILLEGAL")
                    rejectFlag = 5
                    rejectCount += 1
                else:
                    uploadUser(row)

    #the NETHER! (get rid of the file since we are done parsing it)
    os.remove("flaskr/static/userupload.csv")
    userlist = searchBar("", "reset")
    return render_template('user-tools/strappedDash.html', userlist=userlist, warning=rejectFlag, rejectedNumber=rejectCount, totalNumber=userCount)
    #i havent even watched the minecraft movie but these sound bits are rotting my brain as we speak

# def edituser():
# will be used later for when editing an already existing user