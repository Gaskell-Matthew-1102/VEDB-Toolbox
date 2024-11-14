# app/__init__.py

from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from app.config import Config
from app.models import db, Users
from app import routes

def create_app():
    # Initialize Flask app
    app = Flask(__name__, template_folder="../templates", static_folder="../static", instance_relative_config="../instance")

    # Load the configuration from Config class
    app.config.from_object(Config)

    # Initialize database with app
    db.init_app(app)

    # Set up Flask-Bootstrap
    bootstrap = Bootstrap5(app)

    # Set up Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(user_id)

    # Register routes (this can also be modularized into blueprints)
    app.add_url_rule('/', 'home', routes.home)
    app.add_url_rule('/register', 'register', routes.register, methods=["GET", "POST"])
    app.add_url_rule('/login', 'login', routes.login, methods=["GET", "POST"])
    app.add_url_rule('/logout', 'logout', routes.logout)
    app.add_url_rule('/admin-dashboard', 'admin_dashboard', routes.admin_dashboard)

    return app
