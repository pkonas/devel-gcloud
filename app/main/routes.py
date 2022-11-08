from datetime import datetime
import os

from flask import jsonify,render_template, flash, redirect, url_for, send_from_directory
from flask import request
from flask_login import current_user
from flask_login import login_required

from app import db
from app.models import Data, User, VirtualData, InputData
from app.main.forms import EditProfileForm
from app.main import bp

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
@bp.route('/index', methods=["GET", "POST"])
def index():
    return render_template('index.html',title='Home')

@bp.route('/data', methods=["GET", "POST"])
@login_required
def data():
    datas = Data.query
    return render_template('data_table.html', title='Data Table',
                           datas=data)

@bp.route('/simulationdata', methods=["GET", "POST"])
@login_required
def simulationdata():
    datas = VirtualData.query
    return render_template('fmu_table.html', title='Digital twin data table',
                           datas=data)

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
        return redirect(url_for('main.user',username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@bp.route('/favicon.ico')
def favicon():    
    return send_from_directory(os.path.join(bp.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
    