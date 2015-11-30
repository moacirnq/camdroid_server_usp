from flask import Flask, render_template

from flask_mail import Mail
from flask_login import LoginManager
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


from .recorder.recorder import RecordManager
rec_man = RecordManager()
rec_man.start()

def create_app(config_name):

    global rec_man

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    #Custom error pages
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    #Login
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    #Camera
    from .camera import cam as cam_blueprint
    app.register_blueprint(cam_blueprint, url_prefix='/cam')

    #api 0.1
    from .api_0_1 import api as api_0_1_blueprint
    app.register_blueprint(api_0_1_blueprint, url_prefix='/api/v0.1')


    return app
