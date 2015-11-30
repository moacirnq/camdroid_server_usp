from ..models import User
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import  Required, Email, Length, Regexp, EqualTo

class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    email = StringField('Email', validators=[Email(), Required(), Length(1,64)])
    username = StringField('Username', validators=[Required(), Length(1,64),
                Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only'
                                                      'letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required()])
    password2 = PasswordField('Confirm password', validators=[Required(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

