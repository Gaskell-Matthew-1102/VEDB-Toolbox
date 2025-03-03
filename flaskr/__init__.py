"""
1st version of this file was based on a DigitalOcean tutorial that has
since been rewritten constantly to suit our needs. originally a single file
based on that tutorial that has since been split into 5 files.
doing so means this is 100% our (Brian, Leon, Matt, Tyler) work
"""

# app/__init__.py

from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from .config import Config, TestingConfig
from .models import db, Users

# This will avoid circular imports by importing routes here.
def create_app(test_config):
    # Initialize Flask app
    app = Flask(__name__, instance_relative_config=True)

    # Load the configuration from Config class
    if test_config == None:
        app.config.from_object(Config)
    if test_config == True:
        app.config.from_object(TestingConfig)

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

    # Import routes here to avoid circular imports
    with app.app_context():
        from . import auth  # This import depends on the app context being active
        from . import file_upload
        from . import visualizer

        # Register routes (this can also be modularized into blueprints if needed)
        app.add_url_rule('/', 'home', auth.home)
        app.add_url_rule('/landing', 'landing', auth.landing, methods=["GET", "POST"])
        app.add_url_rule('/team', 'team', auth.team)
        app.add_url_rule('/faculty', 'faculty', auth.faculty)        
        app.add_url_rule('/logout', 'logout', auth.logout)

        app.add_url_rule('/dashboard', 'dashboard', auth.dashboard, methods=["GET", "POST"])
        app.add_url_rule('/searchuser', 'searchuser', auth.searchuser, methods=["GET", "POST"])
        app.add_url_rule('/deleteuser', 'deleteuser', auth.deleteuser, methods=["GET", "POST"])
        app.add_url_rule('/adduser', 'adduser', auth.adduser, methods=["GET", "POST"])

        app.add_url_rule('/upload_help', 'upload_help', file_upload.upload_help)
        app.add_url_rule('/upload_video', 'upload_video', file_upload.upload_video, methods=["POST"])
        app.add_url_rule('/upload_data', 'upload_data', file_upload.upload_data, methods=["POST"])
        app.add_url_rule('/upload_video_link', 'upload_video_link', file_upload.upload_video_link, methods=["POST"])
        app.add_url_rule('/upload_data_link', 'upload_data_link', file_upload.upload_data_link, methods=["POST"])
        app.add_url_rule('/upload_different_video', 'upload_different_video', file_upload.upload_different_video, methods=["POST"])
        app.add_url_rule('/upload_different_data', 'upload_different_data', file_upload.upload_different_data, methods=["POST"])
        app.add_url_rule('/go_back', 'back_to_file_upload', file_upload.back_to_file_upload, methods=["POST"])
        app.add_url_rule('/visualizer', 'load_visualizer', file_upload.load_visualizer, methods=[ "POST"])
        
        app.add_url_rule('/exit_visualizer', 'exit_visualizer', visualizer.exit_visualizer, methods=["POST"])

    return app
