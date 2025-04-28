# flask
from flask import Blueprint

blueprint = Blueprint(
    "home", __name__,
    template_folder="templates",
    static_folder="static"
)
