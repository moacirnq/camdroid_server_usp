import cv2

from . import login_manager, db
from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Group_Members(db.Model):
    __tablename__ = 'group_members'
    __table_args__ = (db.ForeignKeyConstraint(['group_owner', 'group_name'], ['groups.owner_id','groups.name'], onupdate='CASCADE', ondelete='CASCADE'),
                      db.ForeignKeyConstraint(['member_id'], ['users.email'], onupdate='CASCADE', ondelete='CASCADE'))
    group_owner = db.Column(db.String(64), primary_key=True)
    group_name = db.Column( db.String(64), primary_key=True)
    member_id = db.Column(db.String(64), primary_key=True)
    group = db.relationship('Group')

class Group(db.Model):
    __tablename__='groups'
    owner_id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64), primary_key=True)
    cameras = db.relationship('Camera')
    # members = db.relationship('members',
    #     secondary='join(Group, Group_Members, Group.owner_id == Group_Members.group_owner, Group.name == Group_Members.group_name)',
    #     lazy='dynamic')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    cameras = db.relationship('Camera', backref='camera')
    groups = db.relationship('Group_Members')
    last_log = db.Column(db.DateTime)

    @property
    def id(self):
        return self.email

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @property
    def shared_cameras(self):
        ret = []
        groups = Group_Members.query.filter_by(member_id=self.email).all()
        for membership in groups:
            for cam in membership.group.cameras:
                ret.append(cam)
        return ret

    def __repr__(self):
        return '<User %r>' % self.username

    def to_json(self):
        all_cameras = []
        for cam in self.cameras:
            all_cameras.append(cam.to_json())
        for cam in self.shared_cameras:
            all_cameras.append(cam.to_json)

        json_user = {
            'url': url_for('api.get_user'),
            'username': self.username,
            'email': self.email,
            'cameras': all_cameras
        }
        return json_user


class Camera(db.Model):
    __tablename__ = 'cameras'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(200))
    src = db.Column(db.String(100))
    username = db.Column(db.String(64))
    password = db.Column(db.String(64))
    owner_id = db.Column(db.String(64), db.ForeignKey('users.email', onupdate='CASCADE', ondelete='CASCADE'))
    height = db.Column(db.Integer)
    width = db.Column(db.Integer)
    group_name = db.Column(db.String(64))
    group_owner = db.Column(db.String(64))
    __table_args__ = (db.ForeignKeyConstraint(['group_owner', 'group_name'], ['groups.owner_id','groups.name'], onupdate='CASCADE', ondelete='CASCADE'),)

    @property
    def link(self):
        ret = ''
        if self.username and self.username != '':
            ret += 'http://' + self.username + ':'
            if self.password and self.password != '':
                ret += self.password + '@'
        if ret != '':
            ret += self.src.replace('http://', '')
        else:
            ret += self.src
        return ret

    def to_json(self):
        json_camera = {
            'id': self.id,
            'name' : self.name,
            'owner': self.owner_id,
            'group': self.group_name,
            'link': self.link,
            'height':self.height,
            'width':self.width
        }
        return json_camera


class VideoFile(db.Model):
    __tablename__ = 'video_files'
    src = db.Column(db.Integer, db.ForeignKey('cameras.id', onupdate='CASCADE', ondelete='CASCADE'))
    camera = db.relationship('Camera')
    path = db.Column(db.String(100), primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def to_json(self):
        return {'src':self.src, 'path': self.path, 'start_time': self.start_time, 'end_time': self.end_time}


class Alert(db.Model):
    __tablename__ = 'alerts'
    camera = db.Column(db.Integer, db.ForeignKey('cameras.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    time = db.Column(db.DateTime, primary_key=True)
    video = db.Column(db.String(100))

    def to_json(self):
        return {'camera':self.camera,
                'time':self.time,
                'video':self.video}


class Camdroid(db.Model):
    __tablename__ = 'camdroids'
    id = db.Column(db.Integer, primary_key = True)
    port = db.Column(db.Integer)