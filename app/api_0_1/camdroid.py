from flask import jsonify, request, g, abort, url_for, current_app

from datetime import datetime

import unicodedata
from . import api
from .. import rec_man
from .authentication import auth, verify_password
from .errors import forbidden
from ..models import Alert, User, Camera, VideoFile, db

start_port = 9001

@api.route('/camdroid/get_port/', methods=['POST'])
@auth.login_required
def get_port(port):
    global start_port
    start_port=+1
    return jsonify{{'Port':start_port}}