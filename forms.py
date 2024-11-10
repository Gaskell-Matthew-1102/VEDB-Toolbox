# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import InputRequired, Length

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=0, max=256)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=0, max=256)])

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=0, max=256)])
    email = EmailField("Email", validators=[InputRequired(), Length(min=0, max=512)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=0, max=256)])
    repeat_password = PasswordField('Repeat Password', validators=[InputRequired(), Length(min=0, max=256)])
