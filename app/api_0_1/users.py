from flask import jsonify, request, g, abort, url_for, current_app

from datetime import datetime

import unicodedata
from . import api
from .. import rec_man
from .authentication import auth, verify_password
from .errors import forbidden
from ..models import Alert, User, Camera, VideoFile, db


@api.route('/user', methods=['GET'])
def login():
    a = request.authorization
    if not a or not verify_password(a.username, a.password):
        return jsonify({'Login':'Failed'})
    else:
        return jsonify({'Login':'OK'})


@api.route('/user', methods=['POST'])
def user_new():
    json = request.json
    email = str(json.get('email'))
    username = str(json.get('username'))
    password = str(json.get('password'))
    new_user = User(email=email, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    ret = jsonify({'Result': 'OK'})
    return ret