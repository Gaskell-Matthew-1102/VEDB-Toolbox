"""
initial version took inspiration GeeksForGeeks tutorial that has
since been reworked to only do database stuff. 100% Brian's work nonetheless
"""

# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(512), nullable=False)
    password = db.Column(db.String(256), nullable=False, default="")
    administrator = db.Column(db.Boolean, default=False)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
