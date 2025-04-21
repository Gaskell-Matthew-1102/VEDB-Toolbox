# by brian

# flask stuff
from flask import url_for, session, redirect, flash, render_template
from flask_login import login_user, current_user, logout_user

# pip other
from werkzeug.security import generate_password_hash, check_password_hash

# local
from flaskr import db, login_manager
from flaskr.models import User
from flaskr.user_auth import blueprint
from flaskr.user_auth.forms import RegistrationForm, LoginForm
from flaskr.user_auth.methods import *

# prerequisite to make things work
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# landing. dual register/sign-in
@blueprint.route('/landing', methods=['GET', 'POST'])
def landing():
    if current_user.is_authenticated:
        return redirect("/file_upload")

    register_form = RegistrationForm()
    login_form = LoginForm()

    if register_form.validate_on_submit():
        # check if user already exists
        if User.query.filter_by(username=register_form.username.data).first():
            register_form.username.data = ''
            register_form.email.data = ''
            register_form.password.data = ''
            register_form.repeat_password.data = ''
            flash("Username already in use.")
            return redirect("/landing")
        else:
            # create user
            user = User(username=register_form.username.data, email=register_form.email.data, password_hash=generate_password_hash(register_form.password.data), admin=is_first_user())
            db.session.add(user)
            db.session.commit()
            flash("Success!")
            login_user(user)
            return redirect("/file_upload")

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and check_password_hash(user.password_hash, login_form.password.data):
            login_user(user)
            flash("Success!")
            return redirect("/file_upload")
        else:
            flash("Invalid username or password.")
            return redirect("/landing")

    return render_template("user_auth/landing.html", login_form=login_form, register_form=register_form, logged_in=current_user.is_authenticated)

# logout clearing session
@blueprint.route("/logout")
def logout():
    logout_user()
    return redirect("/")
