"""
1st version of this file was based on a DigitalOcean tutorial that has
since been rewritten constantly to suit our needs. at this point this is
100% our (Brian, Leon) work
"""

# auth.py

from flask import render_template, redirect, flash, url_for
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Users
from .file_upload import *
from .forms import LoginForm, RegistrationForm
from .search import searchBar

# Home route
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('landing'))
    form1 = True
    form2 = True
    return render_template("file-upload/file_upload.html", show_form1=form1, show_form2=form2)

# Landing route
def landing():
    login_form = LoginForm()
    signup_form = RegistrationForm()

    if signup_form.validate_on_submit():
        # check if user already exists
        if Users.query.filter_by(username=signup_form.username.data).first():
            flash("Username already in use!", "danger")
            return redirect(url_for("register"))   

        # check if passwords match
        if not signup_form.password.data == signup_form.repeat_password.data:
            flash("Passwords not matching!", "danger")
            return redirect(url_for("register"))

        # creates user
        user = Users(username=signup_form.username.data, email=signup_form.email.data, password=generate_password_hash(signup_form.password.data))

        # write to DB
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Welcome.", "success")
        
        # login user after creation
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

    return render_template("auth/landing.html", login_form=login_form, signup_form=signup_form)
    
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

# Dashboard Route
def dashboard():
    user = Users.query.filter_by(username=current_user.username).first()
    if user.administrator:
        userlist = searchBar(request.form.get('user_search', ""))
        headings = ("Username", "Email", "Administrator")
        return render_template('user-tools/dashboard.html', userlist=userlist, headings=headings)
    else:
        return render_template("file-upload/file_upload.html", show_form1=show_form1, show_form2=show_form2)

