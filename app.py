# generously uses https://www.geeksforgeeks.org/how-to-add-authentication-to-your-app-with-flask-login

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# create flask application
app = Flask(__name__)

# define database and secret key for SQLAlchemy to connect to
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_db.sqlite'
app.config['SECRET_KEY'] = 'secret-key'
db = SQLAlchemy()

# setup LoginManager to log users in/out
login_manager = LoginManager()
login_manager.init_app(app)

# create user model
# inherits from db.Model to make it a DB model (duh)
# inherits from UserMixin to provide authentication features
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(512), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False, default="")
    administrator = db.Column(db.Boolean, default=False)

# initialize app with extension
db.init_app(app)

# create DB within app context
with app.app_context():
    db.create_all()

@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

@app.route("/register", methods=["GET", "POST"])
def register():
    # if POST request sent, create new user with provided input.
    if request.method == "POST":
        # check if provided username already exists in DB
        if Users.query.filter_by(username = request.form.get("username")).first():
            flash("Username already in use!", "danger")
            return redirect(url_for("register"))

        # computes and stores password hash
        password_hash = generate_password_hash(request.form.get("password"))
        user = Users(username=request.form.get("username"), email=request.form.get("email"), password=password_hash)

        # add user to DB and commit changes
        db.session.add(user)
        db.session.commit()

        # once account is created, log in as user and redirect to home
        login_user(user)
        return redirect(url_for("home"))

    # else (if GET), render sign_up template
    return render_template("sign_up.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # if POST request sent, search DB by filtering for given username
    if request.method == "POST":
        user = Users.query.filter_by(username = request.form.get("username")).first()

        # check if given password matches the password hash for the given user,
        # logging them in and redirecting them to home (video player).
        # else it sends a flash message saying invalid username/password
        if user and check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Invalid username/password!", "danger")

    # else (if GET), render login template
    return render_template("login.html")

@app.route("/logout")
def logout():
    # returns user back to home
    logout_user()
    return redirect(url_for("home"))
@app.route("/")
def home():
    # render home.html on "/" route
    return render_template("home.html")

if __name__ == "__main__":
    app.run()