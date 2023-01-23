from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, PasswordField
from wtforms.validators import DataRequired, Optional, Email, Length

class SignupForm(FlaskForm):
    """User Sign-up Form."""

    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    


class LoginForm(FlaskForm):
    """Login form."""

    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])