# written by brian

# base
import re

# flask and its plugins
from flask_wtf import FlaskForm, RecaptchaField

# pip, for flask_wtf
from wtforms import StringField, EmailField, PasswordField, SubmitField, ValidationError
from wtforms.validators import InputRequired, Length, EqualTo, Email

def password_complexity_check(form, field):
    password = field.data
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must include at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must include at least one lowercase letter.')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must include at least one digit.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must include at least one special character.')


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=256)])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=12, max=256), password_complexity_check])
    repeat_password = PasswordField("Repeat Password", validators=[InputRequired(), EqualTo('password', message='Passwords must match.')])
    recaptcha = RecaptchaField()
    submit = SubmitField()

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField()
