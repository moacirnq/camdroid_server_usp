from flask import jsonify, request, g, abort, url_for, current_app
from datetime import datetime

from . import api
from .authentication import auth
from .errors import forbidden
from ..models import Alert, User, Camera, db

@api.route('/cameras/list')
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


@api.route('/alerts')
@auth.login_required
def alerts():
    user = g.current_user
    ret = []
    for cam in user.cameras:
        notifications = Alert.query.filter(Alert.time.__str__() >= user.last_log.__str__(), Alert.camera == cam.id).all()
        for alert in notifications:
            ret.append(alert.to_json())
    for cam in user.shared_cameras:
        notifications = Alert.query.filter(Alert.time.__str__() >= user.last_log.__str__(), Alert.camera == cam.id).all()
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
    name = json.get('name')
    link = json.get('link')
    group = json.get('group')
    username = json.get('username')
    password = json.get('password')
    new_cam = User(name=name, src=link, username=username, password=password,
                    owner_id=user, group_name=group, group_owner=user)
    db.session.add(new_cam)
    db.session.commit()
    return jsonify({'URL':url_for('api.get_camera')+new_cam.id})


@api.route('/cameras/get/<id>')
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
def videos(cam_id):
    pass


