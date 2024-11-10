# config.py

import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///user_db.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret-key'