# from flask import jsonify, request, g, abort, url_for, current_app
#
# from . import api
# from .. import rec_man
# from .authentication import auth, verify_password
# from .errors import forbidden
# from ..models import Camdroid, db
#
# from gi.repository import Gst
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
#         Gst.init(None)
#
#         pipeline = Gst.parse_launch(
#             ' udpsrc port=8888 ! application/x-rtp, encoding-name=H264, payload=96 ! rtph264depay ! h264parse ! ' +
#             'avdec_h264 ! theoraenc ! oggmux ! shout2send ip=127.0.0.1 port=' + str(cam.port) + ' password=hackme mount=video.ogv')
#
#         # Start playing
#         pipeline.set_state(Gst.State.PLAYING)
#
#         return jsonify({'Port': cam.port})
