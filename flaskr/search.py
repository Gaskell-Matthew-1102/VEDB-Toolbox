#search.py
from flask_login import login_user, logout_user, current_user
from .models import db, Users
from .file_upload import *

def searchBar(search_filter):
    userList = userMatch(search_filter)
    list = []

    if search_filter == "none":
        list = Users.query.with_entities(Users.username, Users.email, Users.administrator).all()
    elif '@' in search_filter:  #Search by Email
        list = Users.query.with_entities(Users.username, Users.email, Users.administrator).filter_by(email=search_filter).all()
    else:   #Search by username
        for user in userList:
            list = Users.query.with_entities(Users.username, Users.email, Users.administrator).filter_by(username=user).all()
    return list

def userMatch(key):
    listOfUsers = Users.query.with_entities(Users.username).all()
    matchedList = []
    for user in listOfUsers:
        for a in user:  # TEMP FIX NOT PERM JUST CAUSE LISTS ARE BEIN WEIRD
            if key in a:
                matchedList.append(a)
    print(matchedList)
    return matchedList