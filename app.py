# app.py

from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, Users
import routes

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Setup LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

# Register routes
app.add_url_rule('/register', 'register', routes.register, methods=["GET", "POST"])
app.add_url_rule('/login', 'login', routes.login, methods=["GET", "POST"])
app.add_url_rule('/logout', 'logout', routes.logout)
app.add_url_rule('/', 'home', routes.home)

if __name__ == "__main__":
    app.run()
