#search.py
from flask_login import login_user, logout_user, current_user
from .models import db, Users
from .file_upload import *

def searchBar(search_filter, search_type):
    list = []
    if search_filter == "":
        list = Users.query.with_entities(Users.username, Users.email, Users.administrator).all()
    elif search_type == "email":  #Search by Email
        emaiList = emailMatch(search_filter)
        for user in emaiList:
            foundUser = Users.query.with_entities(Users.username, Users.email, Users.administrator).filter_by(email=user).all()
            for a in foundUser:
                list.append(a)
    elif search_type == "username":   #Search by username
        userList = userMatch(search_filter)
        for user in userList:
            foundUser = Users.query.with_entities(Users.username, Users.email, Users.administrator).filter_by(username=user).all()
            for a in foundUser:
                list.append(a)
    return list

def userMatch(key):
    listOfUsers = Users.query.with_entities(Users.username).all()
    matchedList = []
    for user in listOfUsers:
        for a in user:  # TEMP FIX NOT PERM JUST CAUSE LISTS ARE BEIN WEIRD
            if key in a:
                matchedList.append(a)
    return matchedList

def emailMatch(key):
    listOfUsers = Users.query.with_entities(Users.email).all()
    matchedList = []
    for user in listOfUsers:
        for a in user:  # TEMP FIX NOT PERM JUST CAUSE LISTS ARE BEIN WEIRD
            if key in a:
                matchedList.append(a)
    return matchedList