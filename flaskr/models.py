# written by brian.
# database models relevant to the program. explanations:
#   User is to store user credentials returned from the auth0 json.
#    - During use, the json is stored in the Flask session, so we can use that to creat queries
#   SessionHistory stores a UUID as its PK, which corresponds to a subfolder in 'uploads'
#	 - During use, files are uploaded to that directory
#    - Files stay there, allowing the user to delete whole "sessions" at their discretion

# flask bits
from flask_login import UserMixin

# pip packages. connected to Flask-SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# local
from flaskr import db

class User(UserMixin, db.Model):
	__tablename__ = "users"

	# user credentials, ripped from auth0 json
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique=True, nullable=False)
	email = db.Column(db.String, unique=True, nullable=False)
	password_hash = db.Column(db.String, nullable=False)
	admin = db.Column(db.Boolean, nullable=False, default=False)

	# Define relationships to session histories (UUID-folderpaths)
	session_histories = relationship("SessionHistory", backref="user", lazy=True)

class SessionHistory(db.Model):
	__tablename__ = "session_history"

	# metadata; session_id is actually a UUID with a corresponding folder in uploads/
	session_id = db.Column(db.String, primary_key=True)
	user_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=False)
	session_name = db.Column(db.String, nullable=True, default="VEDB Session")
