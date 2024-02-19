from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, BooleanField, StringField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired()])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=StringField('Password',validators=[DataRequired()])
    repeat_password=StringField('Repeat Password',validators=[DataRequired(), EqualTo('password')])
    submit=SubmitField('Register')

    def validate_user(self,username):
        user=db.session.scalar(sa.select(User).where(User.username==username.data))
        if user is not None:
            raise ValidationError('Username taken. Please use a different username.')
    
    def validate_email(self,email):
        user=db.session.scalar(sa.select(User).where(User.email==email.data))
        if user is not None:
            raise ValidationError('Email already used. Please use a different email.')