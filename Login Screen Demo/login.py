import user
from flask import Flask, redirect, request
from flask_login import LoginManager, logout_user

login_manager = LoginManager()

#Reference: https://flask-login.readthedocs.io/en/latest/#flask_login.login_fresh

app = Flask(__name__)
#Replace 5000 here with a different port if necessary
#Eventually refactor this for actual hosting
app.config['SERVER_NAME'] = 'localhost:5000'

#Rename to actual application name
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_email: str):
    return user.User.get(user_email)

def validate_login(username: str, password: str) -> bool:
    # This should hit the DB to check against username and password
    # dummy data used here instead
    
    dummyUser = "waltuh"
    dummyPass = "white"

    return(username == dummyUser and password == dummyPass)

#Rename to application name
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        print(f"Username: {request.form['username']} | Password: {request.form['password']}")
        if validate_login(request.form['username'], request.form['password']):
            print("Login validated")
            return log_the_user_in(request.form['username'])
        else:
            print("Login failed to validate")
            error = 'Invalid username/password'
    return render_template('login.html', error=error)

#Rename to application name, rename redirect
@app.route('/logout')
def logout():
    logout_user()
    return redirect(somewhere)

@app.route("/")
def guh():
    return "<p>hi<p>"

if __name__ == "__main__":
    app.run()
print("how did we get here")