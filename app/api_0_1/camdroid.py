# #Flask stuff
# from flask import jsonify, request, g, abort, url_for, current_app
#
# #Internal stuff
# from . import api
# from .. import rec_man
# from .authentication import auth, verify_password
# from .errors import forbidden
# from ..models import Camdroid, Camera, db
#
# #GStreamer livs
# #import gst as gstCam
# import os
#
# #IP Stuff
# import netifaces as ni
#
# @api.route('/camdroid/get_port/<id>', methods=['GET', 'POST'])
# @auth.login_required
# def get_port(id):
#     cam = Camdroid.query.filter_by(id=id).first()
#     if cam is None:
#         response = jsonify({'error':'bad request', 'message':'Camera does not exist.'})
#         response.status_code = 400
#         return response
#     else:
#
#         # pipeline = gstCam.parse_launch( \
#         #     ' udpsrc port=' + str(cam.port) + ' ! application/x-rtp, encoding-name=H264, payload=96 ! rtph264depay ! h264parse ! ' +
#         #      'decodebin ! theoraenc ! oggmux ! shout2send ip=127.0.0.1 port=8000 password=hackme mount='+ str(cam.id) +'.ogv')
#
#         # Start playing
#         # pipeline.set_state(gstCam.STATE_PLAYING)
#
#         # os.spawnl(os.P_NOWAIT, "gst-launch-0.10 udpsrc port=" + str(cam.port) + " ! application/x-rtp, encoding-name=H264, payload=96 ! rtph264depay " +
#         #           "! h264parse ! decodebin ! theoraenc ! oggmux ! shout2send ip=127.0.0.1 port=8000 password=hackme mount=" + str(cam.id) + ".ogv")
#
#         os.spawnl(os.P_NOWAIT, "v4l2src ! theoraenc ! oggmux ! shout2send ip=127.0.0.1 port=8000 password=hackme mount=" + str(cam.id) + ".ogv")
#
#
#         new_cam = Camera(name= 'Camdroid' + str(cam.id),
#                      group_name= 'default',
#                      group_owner=g.current_user.email,
#                      description = 'Camdroid',
#                      src= 'http://' + get_ip_address('wlp1s0') + ':8000/' +str(cam.id) +'.ogv',
#                      height=240,
#                      width=320,
#                      password=None,
#                      username=None,
#                      owner_id=g.current_user.id)
#         db.session.add(new_cam)
#         db.session.commit()
#
#         rec_man.add_camera(new_cam)
#
#         return jsonify({'Port': cam.port})
#
#
# def get_ip_address(ifname):
#     your_ip = ni.ifaddresses(ifname)[2][0]['addr']
#     return your_ip