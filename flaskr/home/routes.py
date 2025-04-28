# written by brian, basic routing table for the "dumb" pages

# flask
from flask import render_template

# local
from flaskr.home import blueprint
from flaskr.home.methods import *

@blueprint.route("/")
def home():
    return render_template("home/home.html", logged_in=is_logged_in())

@blueprint.route("/team")
def team():
    return render_template("home/team.html", logged_in=is_logged_in())

@blueprint.route("/faculty")
def faculty():
    return render_template("home/faculty.html", logged_in=is_logged_in())

@blueprint.route("/tutorial")
def tutorial():
    return render_template("home/tutorial.html", logged_in=is_logged_in())

@blueprint.app_errorhandler(404)
def page_not_found(e):
    return render_template("home/404.html"), 404

@blueprint.app_errorhandler(500)
def something_went_wrong(e):
    return render_template("home/500.html"), 500
