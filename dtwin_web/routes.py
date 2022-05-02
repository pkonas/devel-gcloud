# -*- coding: utf-8 -*-
from dtwin_web import app
from flask import render_template, make_response, flash, redirect, url_for
import json
from dtwin_web import db
from dtwin_web.models import Data,User
from flask_login import current_user, login_user, logout_user
from dtwin_web.forms import LoginForm, RegistrationForm
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse

@app.route('/')
def index():
    return render_template('index.html', title='Temperature and humidity')

@app.route('/data', methods=["GET", "POST"])
@login_required            
def data(): 
    obj = db.session.query(Data.datetime, Data.temperature, Data.humidity).order_by(db.desc('datetime')).first()        
    Temperature = obj[1]
    Humidity = obj[2]
    data = [(obj[0] + 7200) * 1000, Temperature, Humidity] #uprava casu aby ukazaoval +2h
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

@app.route('/setup', methods=["GET", "POST"])
@login_required
def setup():   
    rq_job = app.task_queue.enqueue('dtwin_web.server.start_server',job_timeout=-1)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)