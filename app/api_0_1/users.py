from flask import jsonify, request, g, abort, url_for, current_app

from datetime import datetime

import unicodedata
from . import api
from .. import rec_man
from .authentication import auth, verify_password
from .errors import forbidden
from ..models import Alert, User, Camera, VideoFile, Group_Members, Group, db


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


@api.route('/user/groups')
@auth.login_required
def groups_get():
    user_email =g.current_user.email
    user = User.query.filter_by(email=user_email).first()
    if user is None:
        response = jsonify({'error':'bad request', 'message':'User does not exist.'})
        response.status_code = 400
        return response
    else:
        ret = []
        for group in user.groups:
            ret.append(group.name)
        return jsonify({'groups': user.groups})


@api.route('/user/groups/add/<group_name>', methods=['POST'])
@auth.login_required
def group_new(group_name):
    try:
        group = Group(owner_id=g.current_user.email, name=group_name)
        db.session.add(group)
        db.session.commit()
        return jsonify({'Result':'New group added.'})
    except Exception as e:
        return jsonify({'Result:': ('Exception\n:' + e.message)})


@api.route('/user/groups/remove/<group_name>', methods=['POST'])
@auth.login_required
def group_remove(group_name):
    try:
        group = Group.query.filter_by(name=group_name, owner_id=g.current_user.email).first()
        if group is not None:
            db.session.delete(group)
            db.session.commit()
        return jsonify({'Result':'Group removed.'})
    except Exception as e:
        return jsonify({'Result:': ('Exception\n:' + e.message)})


@api.route('/user/groups/add/member/', methods=['POST'])
@auth.login_required
def group_member_new():
    json = request.json
    group_name = json['group_name']
    member_email = json['member']
    try:
        group = Group(owner_id=g.current_user.email, name=group_name)
        user = User.query.filter_by(email=member_email)
        membership = Group_Members(group_owner=g.current_user.email,
                                   group_name=group_name,
                                   member_id=member_email)
        db.session.add(membership)
        db.session.commit()
        return jsonify({'Result':'New member added.'})
    except Exception as e:
        return jsonify({'Result:': ('Exception\n:' + e.message)})



@api.route('/user/groups/get_members/<group_name>')
@auth.login_required
def group_members_get(group_name):
    try:
        group = Group.query.filter_by(name=group_name, owner_id=g.current_user.email)
        members=Group_Members.query.filter_by(group_owner=g.current_user.email, group_name=group_name).all()
        ret = []
        for member in members:
            ret.append(member.member_id)

        return jsonify({'members':ret})

    except Exception as e:
        return jsonify({'Result:': ('Exception\n:' + e.message)})