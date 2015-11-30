from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import Required

class CameraRegistrationForm(Form):
    name = StringField('Camera name', validators=[Required()])
    src = StringField('Link to video', validators=[Required()])
    group = SelectField('Group')
    username = StringField('Username', validators=[])
    password = PasswordField('Password', validators=[])
    description = TextAreaField('Description')
    submit = SubmitField('Register')

class NewGroupRegistrationForm(Form):
    name = StringField('Name', validators=[Required()])
    submit = SubmitField('Register')

class GroupMemberRegistrationForm(Form):
    member = StringField('Email:', validators=[Required()])
    submit = SubmitField('Add Member')