from datetime import datetime
import time
import threading

from flask import current_app
from flask import render_template, flash, redirect, url_for
from flask import request
from flask_login import current_user
from flask_login import login_required

from app import db
from app import turbo
from app.models import Data, User, FmuData
from app.main.forms import EditProfileForm, ValveForm
from app.main import bp, valve_opening
from app.main.charts import livecharts, history_chart

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    
# @bp.before_request
# def before_first_request():
#     threading.Thread(target=update_load).start()

# def update_load():
#     with current_app.app_context:
#         while True:
#             time.sleep(5)
#             turbo.push(turbo.replace(render_template('index.html'), 'data'))

@bp.route('/')
@bp.route('/index', methods=["GET", "POST"])
def index():
    data = FmuData.query.order_by(FmuData.datetime.desc()).first().to_dict()
    print(data)
    return render_template('index.html',data=data,title='Home')

@bp.route('/charts', methods=["GET", "POST"])
def charts():
    script, div = livecharts()
    return render_template('charts.html',script=script, div=div, title='Hydraulic live')

@bp.route('/history', methods=["GET", "POST"])
def history():
    script, div = history_chart()
    return render_template('history.html',script=script, div=div,title='History')

@bp.route('/data', methods=["GET", "POST"])
@login_required            
def data(): 
    datas = Data.query
    return render_template('data_table.html', title='Data Table',
                           datas=datas)

@bp.route('/simulationdata', methods=["GET", "POST"])
@login_required            
def simulationdata(): 
    datas = FmuData.query
    return render_template('fmu_table.html', title='Digital twin data table',
                           datas=datas)

@bp.route('/setvalve', methods=["GET", "POST"])
@login_required
def set_valve():
    form = ValveForm()
    if request.method == 'POST':
        valve_opening.current_value = form.valve_opening.data
        print(valve_opening.current_value)
        flash('Control valve opening has been set!')
        #return redirect(url_for('main.charts'))
    return render_template('set_valve.html', form=form,title='Control valve')       

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
    