# routes.py

from flask import render_template, redirect, flash, url_for
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Users
from forms import LoginForm, RegistrationForm

# Register route
def register():
    # create WTForm instance
    form = RegistrationForm()

    if form.validate_on_submit():
        # check if user already exists
        if Users.query.filter_by(username=form.username.data).first():
            flash("Username already in use!", "danger")
            return redirect(url_for("register"))   

        # check if passwords match
        if not form.password.data == form.repeat_password.data:
            flash("Passwords not matching!", "danger")
            return redirect(url_for("register"))

        # creates user
        user = Users(username=form.username.data, email=form.email.data, password=generate_password_hash(form.password.data))

        # write to DB
        db.session.add(user)
        db.session.commit()

        # login user after creation
        login_user(user)
        flash("Registration successful! Welcome.", "success")
        return redirect(url_for("home"))

    return render_template("register.html", form=form)

# Login route
def login():
    # Create LoginForm (WTForm)
    form = LoginForm()

    if form.validate_on_submit():
        # Query DB for first user with inputted username
        user = Users.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username/password!", "danger")

    return render_template("login.html", form=form)

# Logout route
def logout():
    logout_user()
    return redirect(url_for("home"))

# Home route
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))  # Redirect to the login page if the user is not logged in
    return render_template("home.html")

# placeholder for administration dashboard