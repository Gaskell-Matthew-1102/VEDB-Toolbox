# routes.py

from flask import render_template, redirect, flash, url_for
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, Users
from app.forms import LoginForm, RegistrationForm

# Home route
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template("home.html")

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

    return render_template("login/register.html", form=form)

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

    return render_template("login/login.html", form=form)

# Logout route
def logout():
    logout_user()
    return redirect(url_for("home"))

# Dashboard Route
def admin_dashboard():
    # to leon. work on making this not display the password hashes. bc why
    users = Users.query.all()
    return render_template('user-tools/admin-dashboard.html', users=users, Users=Users)