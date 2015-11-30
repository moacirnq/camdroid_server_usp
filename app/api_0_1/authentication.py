from flask import g
from flask_httpauth import HTTPBasicAuth
from datetime import datetime

from .errors import *
from ..models import User

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email, password):
    if email == '':
        return False
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    user.last_log = datetime.now()
    g.current_user = user
    return user.verify_password(password)

@auth.error_handler
def error_handler():
    return unauthorized('Invalid')