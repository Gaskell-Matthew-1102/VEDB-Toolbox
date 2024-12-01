#search.py
from flask_login import login_user, logout_user, current_user
from .models import db, Users
from .file_upload import *

def searchBar(search_filter):
    if search_filter == "none":
        list = Users.query.with_entities(Users.username, Users.email, Users.administrator).all()
    elif '@' in search_filter:
        list = Users.query.with_entities(Users.username, Users.email, Users.administrator).filter_by(email=search_filter).all()
    else:
        list = Users.query.with_entities(Users.username, Users.email, Users.administrator).filter_by(username=search_filter).all()
    return list
