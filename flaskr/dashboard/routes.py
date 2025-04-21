# written by leon, organized into new structure by brian

# base
from os import remove as remove_file
from os import rename as rename_file

# flask and its plugins
from flask import redirect, request
from flask_login import current_user

# local
from flaskr.models import User
from flaskr.dashboard import blueprint
from flaskr.dashboard.methods import *

# Dashboard Route
@blueprint.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = User.query.filter_by(username=current_user.username).first()
    if user.admin:
        return render_dashboard("", "reset", 0)
    else:
        return redirect("/file_upload")

@blueprint.route("/searchuser", methods=["GET", "POST"])
def searchuser():
    if request.form["formType"] == "email":   #Search through email bar
        return render_dashboard(request.form.get('email_search', ""), "email", 0)
    elif request.form["formType"] == "username":  #search through username bar
        return render_dashboard(request.form.get('user_search', ""), "username", 0)
    else:   #reset search
        return render_dashboard("", "reset", 0)

@blueprint.route("/adduser", methods=["GET", "POST"])
def adduser():
    # check if user already exists
    if User.query.filter_by(username=request.form.get('unEnter', "")).first():
        flash("Username already in use!", "danger")
        return render_dashboard("", "reset", 1)
    else:
        uploadedUserData = [request.form.get('unEnter', ""), request.form.get('emEnter', ""), request.form.get('pwEnter', ""), request.form.get('admEnter', ""), request.form.get('admEnter', "")]
        #print(request.form.get('admEnter', ""))
        upload_user(uploadedUserData)
        return render_dashboard("", "reset", 2)

@blueprint.route("/deleteuser", methods=["GET", "POST"])
def deleteuser():
    deleting = request.form.get('user_to_delete', "")
    foundUser = User.query.with_entities(User.id).filter_by(username=deleting).all()

    #As of now, foundUser is a list with a list with the id
    for a in foundUser:
        for b in a:
            #refuses to delete account if the account being deleted is the one using to delete
            #basically, you cannot delete yourself
            if b == current_user.id:
                return render_dashboard(request.form.get('user_search', ""), "username", 4)
            #otherwise, continue through with deletion
            else:
                User.query.filter_by(id=b).delete()
                db.session.commit()
    
    return render_dashboard(request.form.get('user_search', ""), "username", 3)

@blueprint.route("/csvupload", methods=["GET", "POST"])
def csvupload():
    rejectFlag = 2
    rejectCount = 0
    userCount = 0
    #thanks matt
    #THIS, is a CRAFTING TABLE. (save the file)
    if request.method == 'POST':
        file_link = request.files['filename']
        file_link.save(file_link.filename)
        name =  file_link.filename

    #first, we MINE! (let's verify the file itself before we parse it)
        if not verify_csv(name): #if not the correct file,
            remove_file(name) #remove incorrect file
            return render_dashboard("", "reset", 1)

        rename_file(name, "flaskr/static/userupload.csv")

    #then we CRAFT! (parse the csv file data)
        with open("flaskr/static/userupload.csv", newline='') as csvfile:
            listOfUsers = csv.reader(csvfile, delimiter=',', quotechar='|')

    #flint and STEEL! (we check to see if the data itself is valid, specifically the username)
            for row in listOfUsers:
                userCount += 1
                if User.query.filter_by(username=row[0]).first():  #reject if list has an existing user already
                    print("no it is now ILLEGAL")
                    rejectFlag = 5
                    rejectCount += 1
                else:
                    upload_user(row)

    #the NETHER! (get rid of the file since we are done parsing it)
    remove_file("flaskr/static/userupload.csv")
    return render_dashboard("", "reset", rejectFlag, rejectedNumber=rejectCount, totalNumber=userCount)
    #i haven't even watched the minecraft movie but these sound bits are rotting my brain as we speak

# def edituser():
# will be used later for when editing an already existing user
