# -*- coding: utf-8 -*-
from dtwin_web import app
from flask import render_template, make_response
import json
from dtwin_web import db
from dtwin_web.models import Data

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/data', methods=["GET", "POST"])            
def data(): 
    obj = db.session.query(Data.datetime, Data.temperature, Data.humidity).order_by(db.desc('datetime')).first()  
    print(obj)      
    Temperature = obj[1]
    Humidity = obj[2]
    data = [(obj[0] + 7200) * 1000, Temperature, Humidity] #uprava casu aby ukazaoval +2h
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response