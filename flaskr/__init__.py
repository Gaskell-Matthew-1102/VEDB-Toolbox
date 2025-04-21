# written by brian
# this file serves as the system "master", doing:
#   connecting with the subsystems (Flask Blueprints)
#   registering all the extensions used in the application
#   minifies everything to serve it easier
# this rewrite was made possible with:
# guide: https://hackersandslackers.com/flask-application-factory/
# guide: https://github.com/app-generator/flask-datta-able

# base
from importlib import import_module

# flask and its plugins
from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_minify import Minify
from flask_wtf.csrf import CSRFProtect

# globally accessible objects
db = SQLAlchemy()
csrf = CSRFProtect()
bootstrap = Bootstrap5()
login_manager = LoginManager()

def register_extensions(app):
    db.init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

# registers blueprints in a generalized manner. idea by chatgpt
def register_blueprints(app, bp_list):
    for module_name in bp_list:
        module = import_module('flaskr.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

def create_app(test_config=None):
    # initialize core application
    app = Flask(__name__, instance_relative_config=True)

    # configuration
    if test_config is None:
        app.config.from_object("flaskr.config.Config")
    elif test_config:
        app.config.from_object("flaskr.config.TestingConfig")

    # minifies files within the project for faster serving
    Minify(app, html=True, js=True, cssless=True)

    register_extensions(app)

    # blueprints. these are the aforementioned "subsystems" found in our project
    blueprint_list = ["home", "user_auth", "file_upload", "visualizer", "dashboard"]
    register_blueprints(app, blueprint_list)

    with app.app_context():
        db.create_all()
        
    return app
