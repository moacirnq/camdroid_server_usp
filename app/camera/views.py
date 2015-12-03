from flask import render_template, session, redirect, url_for, current_app, flash, send_from_directory
from flask_login import current_user
from .forms import CameraRegistrationForm, NewGroupRegistrationForm, GroupMemberRegistrationForm

from .. import db, rec_man
from ..camera import cam
from ..recorder.recorder import CameraRecoder, RecordManager
from ..models import Camera, Group, Group_Members, User, VideoFile
from ..mail import send_email
from flask.ext.login import login_required

@cam.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = CameraRegistrationForm()
    form.group.choices = [ (g.name, g.name) for g in Group.query.filter_by(owner_id = current_user.email).all()]
    if form.validate_on_submit():
        #try:
        cam = Camera(name=form.name.data,
                     group_name=form.group.data,
                     group_owner=current_user.email,
                     description = form.description.data,
                     src=form.src.data,
                     height=form.height.data,
                     width=form.width.data,
                     password=form.password.data,
                     username=form.username.data,
                     owner_id=current_user.id)
        db.session.add(cam)
        db.session.commit()
        flash('Camera registered.')
        rec_man.add_camera(cam)
        #except Exception, e:
            #flash('Error on camera register\n.' + e.message)
    return render_template('cam/register.html', form=form)

@cam.route('/update/<cam_id>', methods=['GET', 'POST'])
@login_required
def update(cam_id):
    form = CameraRegistrationForm()
    form.group.choices = [ (g.name, g.name) for g in Group.query.filter_by(owner_id = current_user.email).all()]
    cam = Camera.query.filter_by(id=cam_id).first()
    if cam.owner_id != current_user.email:
        flash('Camera not found.')
        redirect('/index.html')
    if form.validate_on_submit():
        #try:
        cam.name = form.name.data
        cam.group_name = form.group.data
        cam.description = form.description.data
        cam.src = form.src.data
        cam.password = form.password.data
        cam.username = form.username.data
        cam.width = form.width.data
        cam.height = form.width.data
        db.session.add(cam)
        db.session.commit()
        flash('Camera updated.')
        rec_man.add_camera(cam)
    else:
        form.name.data = cam.name
        form.group.data = cam.group_name
        form.description.data = cam.description
        form.src.data = cam.src
        form.password.data = cam.password
        form.username.data = cam.username
    return render_template('cam/register.html', form=form)


@cam.route('/list')
@login_required
def list():
    group_dic = {}
    groups = Group_Members.query.filter_by(member_id=current_user.email).all()
    for membership in groups:
        group_dic[membership.group_name] = membership.group.cameras
    return render_template('cam/list.html', cameras=current_user.cameras, shared_cams=group_dic)

@cam.route('/videos/<cam_id>')
@login_required
def videos(cam_id):
    id = int(cam_id);
    videos = VideoFile.query.filter_by(src=id).all()
    return render_template('cam/videos.html', videos=videos)



@cam.route('/delete/<camera_id>')
@login_required
def delete(camera_id):
    cam =  Camera.query.filter_by(id=camera_id).first()
    if cam and cam.owner_id == current_user.id:
        rec_man.remove_camera(cam)
        db.session.delete(cam)
        db.session.commit()
        flash('Camera '+cam.name+' removed.')
    else:
        flash('Error removing camera. Check if the camera exists or if you have the right permissions to do it.')
    return redirect(url_for('cam.list'))

#todo
@cam.route('/details/<camera_id>')
@login_required
def details(camera_id):
    cam =  Camera.query.filter_by(id=camera_id).first()
    if cam and cam.owner_id == current_user.id:
        return redirect('cam/details.html', camera=cam)
    else:
        flash('Error removing camera. Check if the camera exists or if you have the right permissions to do it.')
    return redirect(url_for('cam.list'))

@cam.route('/group/new', methods=['GET','POST'])
@login_required
def group_new():
    form = NewGroupRegistrationForm()
    if form.validate_on_submit():
        #try:
        group = Group.query.filter_by(owner_id=current_user.email, name=form.name.data).all()
        if not len(group):
            group = Group(owner_id=current_user.email,
                      name=form.name.data)
            db.session.add(group)
            db.session.commit()
            flash('Group ' + form.name.data + ' created.' )
            return redirect(url_for('cam.group_list'))
        flash('Group could not be created.')
    return render_template('cam/group/new.html', form=form)


@cam.route('/group/list')
@login_required
def group_list():
    my_groups = Group.query.filter_by(owner_id=current_user.email)
    return render_template('cam/group/list.html', my_groups=my_groups)


@cam.route('/group/remove/<name>')
@login_required
def group_remove(name):
    group = Group.query.filter_by(owner_id=current_user.email, name=name).first()
    if group:
        db.session.delete(group)
        db.session.commit()
        flash('Group ' + name + ' deleted.')
    return render_template('index.html')

@cam.route('/group/member/add/<group_name>', methods=['GET','POST'])
@login_required
def group_details(group_name):
    form = GroupMemberRegistrationForm()
    group = Group.query.filter_by(name=group_name, owner_id=current_user.email)
    members=Group_Members.query.filter_by(group_owner=current_user.email, group_name=group_name).all()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.member.data).first()
        if user is not None:
            member = Group_Members(group_owner=current_user.email,
                                   group_name=group_name,
                                   member_id=form.member.data)
            db.session.add(member)
            db.session.commit()
            flash('User ' + member.member_id + ' added to group.')
        else:
            flash('User not found.')

    return render_template('cam/group/details.html', form=form, members=members, group=group_name)