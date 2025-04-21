# flask
from flask import Blueprint

blueprint = Blueprint(
    "file_upload", __name__,
    template_folder="templates",
    static_folder="static"
)
