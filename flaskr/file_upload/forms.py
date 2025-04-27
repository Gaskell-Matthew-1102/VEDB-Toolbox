# written by brian
# defined basic URL input fields as to avoid literally creating a HTML form
# avoids directly checking POST requests in routes.py.
# defined WTForm classes for URL input as to:
#   avoid literally creating an HTML form on the page and generating a POST request
#    - in the original write, this was the case. rather unwieldy!

# base
from urllib.parse import urlparse

# flask (plugins)
from flask_wtf import FlaskForm

# pip. used for above
from wtforms import URLField, SubmitField, BooleanField, IntegerField, DecimalField
from wtforms.validators import DataRequired, URL, ValidationError

# Custom validator class implementing what used to be "validate_link" in methods.py
# This validates that the link submitted is an appropriate one. "pre-validates" it before submit
class LinkDomainValidator:
    def __init__(self, flag: int, message: str = None) -> None:
        self.flag = flag
        self.expected_domains = {
            0: "databrary.org",
            1: "osf.io"
        }
        self.message = message or "Invalid URL domain."

    def __call__(self, form, field):
        link = field.data
        netloc = urlparse(link).netloc.lower()
        expected_domain = self.expected_domains.get(self.flag)

        if expected_domain is None:
            raise ValidationError("Validator configuration error: invalid flag.")

        if not (netloc == expected_domain or netloc.endswith(f".{expected_domain}")):
            raise ValidationError(self.message)

# Form for Databrary URLs
class DatabraryURLForm(FlaskForm):
    dtb_url = URLField("Databrary URL", validators=[
        DataRequired(),
        URL(),
        LinkDomainValidator(flag=0, message="URL must be from databrary.org")]
    )
    dtb_submit = SubmitField("Submit URL")

# Form for OSF URLs
class OSFURLForm(FlaskForm):
    osf_url = URLField("OSF URL", validators=[
        DataRequired(),
        URL(),
        LinkDomainValidator(flag=1, message="URL must be from osf.io")]
    )
    osf_submit = SubmitField("Submit URL")


class ResetFileUpload(FlaskForm):
    reset = SubmitField("Remove all uploaded files in session")

class FixationParameters(FlaskForm):
    gaze_window_size_ms = IntegerField("Gaze Window Size (ms)", default=55)
    polynomial_grade = IntegerField("Polynomial Grade", default=3)
    min_velocity_threshold = IntegerField("Minimum Velocity Threshold (px/sec)", default=750)
    gain_factor = DecimalField("Gain Factor", default=0.8)
    world_camera_fov_h = IntegerField("World Camera FOV - Horizontal (deg)", default=90)
    world_camera_fov_v = IntegerField("World Camera FOV - Vertical (deg)", default=90)
    eye_camera_fov_h = IntegerField("Eye Camera FOV - Horizontal (deg)", default=110)
    min_saccade_amp_deg = DecimalField("Minimum Saccade Amplitude (deg)", default=1.0)
    min_saccade_dur_ms = IntegerField("Minimum Saccade Duration (ms)", default=10)
    min_fixation_dur_ms = IntegerField("Minimum Fixation Duration (ms)", default=70)
    
    optic_flow_override = BooleanField('Enable IMU Flag Switch', default=False)
    imu_flag = BooleanField("LUCAS (fallback) or IMU?", default=False)

    submit_parameters = SubmitField("Set Fixation Parameters")

class EnterVisualizer(FlaskForm):
    submit = SubmitField("Enter Visualizer")
