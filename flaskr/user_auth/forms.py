# written by brian

# flask and its plugins
from flask_wtf import FlaskForm, RecaptchaField

# pip, for flask_wtf
from wtforms import StringField, EmailField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=256)])
    email = EmailField("Email", validators=[InputRequired(), Length(min=5, max=512)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=12, max=256)])
    repeat_password = PasswordField("Repeat Password", validators=[InputRequired(), Length(min=12, max=256), EqualTo('password', message='Passwords must match.')])
    recaptcha = RecaptchaField()
    submit = SubmitField()

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=256)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=12, max=256)])
    recaptcha = RecaptchaField()
    submit = SubmitField()
