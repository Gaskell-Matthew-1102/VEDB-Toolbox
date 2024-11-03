import flask
import user
from flask import redirect, Flask
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
def load_user(user_email: str)
    return user.get(user_email)

@app.route('/login', methods=['GET', 'POST'])
def login():

    #These lines may need to be connected up to a database
    form = LoginForm()
    if form.validate_on_submit():
        login_user()

        flask.flash('Successfully logged in!')

        next = flask.request.args.get('next')

        #can maybe comment out, or write function for eventual actual hosted url
        if not url_has_allowed_host_and_scheme(next, request.host):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)

#Rename redirect
@app.route('/logout')
def logout():
    logout_user()
    return redirect(somewhere)