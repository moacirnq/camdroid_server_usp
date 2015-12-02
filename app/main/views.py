from flask import render_template, session, redirect, url_for, current_app
from threading import Thread

from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..mail import send_email
from .. import rec_man
from flask.ext.login import login_required


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed.'


@main.route('/add_all', methods=['GET', 'POST'])
def all():
    rec_man.add_all()
    return render_template('index.html')