from flask import jsonify, request, g, abort, url_for, current_app

from datetime import datetime

import unicodedata
from . import api
from .. import rec_man
from .authentication import auth, verify_password
from .errors import forbidden
from ..models import Alert, User, Camera, VideoFile, db


@api.route('/cameras/list', methods=['GET'])
@auth.login_required
def list():
    cameras  = g.current_user.cameras
    shared_cameras = g.current_user.shared_cameras
    all_cameras = []

    for cam in cameras:
        all_cameras.append(cam.to_json())
    for cam in shared_cameras:
        all_cameras.append(cam.to_json())

    return jsonify({ 'list': all_cameras })


@api.route('/alerts', methods=['GET'])
@auth.login_required
def alerts():
    ret = []
    user = User.query.filter_by( email=g.current_user.email).first()
    print user.last_log.__str__()
    for cam in user.cameras:
        notifications = Alert.query.filter(Alert.time >= user.last_log.__str__()).filter(Alert.camera == cam.id).all()
        for alert in notifications:
            ret.append(alert.to_json())
    for cam in user.shared_cameras:
        notifications = Alert.query.filter(Alert.time >= user.last_log.__str__()).filter(Alert.camera == cam.id).all()
        for alert in notifications:
            ret.append(alert.to_json())

    user.last_log = datetime.now()
    db.session.add(user)
    db.session.commit()

    return jsonify({'alerts':ret})


@api.route('/cameras/add', methods=['POST'])
@auth.login_required
def add_camera():
    json = request.json
    user = g.current_user.email
    name = str(json.get('name'))
    link = str(json.get('link'))
    group = str(json.get('group'))
    username = str(json.get('username'))
    password = str(json.get('password'))
    new_cam = Camera(name=name, src=link, username=username, password=password,
                    owner_id=user, group_name=group, group_owner=user)
    db.session.add(new_cam)
    db.session.commit()
    ret =  jsonify({'URL': str(url_for('api.get_camera', id=new_cam.id))})
    print ret
    return ret

@api.route('/cameras/get/<id>', methods=['GET'])
@auth.login_required
def get_camera(id):
    cam = Camera.query.filter_by(id=id).first()
    if cam is None:
        response = jsonify({'error':'bad request', 'message':'Camera does not exist.'})
        response.status_code = 400
        return response
    else:
        return jsonify(cam.to_json())


@api.route('/videos/<cam_id>')
@auth.login_required
def videos(cam_id):
    cam = Camera.query.filter_by(id=cam_id).first()
    if cam is None:
        response = jsonify({'error':'bad request', 'message':'Camera does not exist.'})
        response.status_code = 400
        return response

    videos = VideoFile.query.filter_by(src=cam_id)
    ret = [video.to_json() for video in videos]
    return jsonify({'videos': ret})


@api.route('/cameras/remove/<cam_id>', methods=['POST'])
@auth.login_required
def remove_camera(cam_id):
    cam =  Camera.query.filter_by(id=cam_id).first()
    if cam and cam.owner_id == g.current_user.id:
        rec_man.remove_camera(cam)
        db.session.delete(cam)
        db.session.commit()
        return jsonify({'Result': 'OK'})
    else:
        response = jsonify({'error':'bad request', 'message':'Camera does not exist.'})
        response.status_code = 400
        return response


