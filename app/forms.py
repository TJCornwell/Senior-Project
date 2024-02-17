from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, BooleanField, StringField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    #password confirm?
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')