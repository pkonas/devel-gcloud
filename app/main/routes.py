# -*- coding: utf-8 -*-
from flask import current_app
from flask import render_template, flash, redirect, url_for
from app import db
from app.models import Data,User
from flask_login import current_user
from app.main.forms import EditProfileForm
from flask_login import login_required
from flask import request
from datetime import datetime
from app.main import bp

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/charts')
def charts():
    return render_template('charts.html', title='Temperature and humidity')

@bp.route('/data', methods=["GET", "POST"])
@login_required            
def data(): 
    datas = Data.query
    return render_template('data_table.html', title='Data Table',
                           datas=datas)

@bp.route('/setup', methods=["GET", "POST"])
@login_required
def setup():   
    rq_job = current_app.task_queue.enqueue('app.server.start_server',job_timeout=-1)

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)