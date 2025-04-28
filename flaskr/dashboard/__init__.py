# flask
from flask import Blueprint

blueprint = Blueprint(
    "dashboard", __name__,
    template_folder="templates",
    static_folder="static"
)
