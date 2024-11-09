# routes.py

from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Users

# Register route
def register():
    if request.method == "POST":
        if Users.query.filter_by(username=request.form.get("username")).first():
            flash("Username already in use!", "danger")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(request.form.get("password"))
        user = Users(username=request.form.get("username"), email=request.form.get("email"), password=password_hash)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("home"))

    return render_template("sign_up.html")

# Login route
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()

        if user and check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username/password!", "danger")

    return render_template("login.html")

# Logout route
def logout():
    logout_user()
    return redirect(url_for("home"))

# Home route
def home():
    return render_template("home.html")
