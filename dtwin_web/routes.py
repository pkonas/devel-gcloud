# -*- coding: utf-8 -*-
from dtwin_web import app
from flask import render_template, make_response
from random import random
import time, datetime
import json
import socket
import struct
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
    data = [obj[0] * 1000, Temperature, Humidity]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

@app.route('/server', methods=["GET", "POST"])    
def server():
    hostname, port = "", int(5001)
    print(f"Starting up on {hostname} port {port}")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((hostname, port)) 
    s.listen(1)
    
    while True:
        print("Waiting for connection")
        clientsocket, address = s.accept()
        try:
            print(f"Connection from {address} has been established.")
            while True:            
                packet = clientsocket.recv(1024)
                if packet:
                    data = struct.unpack('!ddd', packet)
                    print(f"Data recieved: {data}")
                    add_data = Data(datetime=data[0],temperature=data[1],humidity=data[2])
                    db.session.add(add_data)
                    db.session.commit()
                else:
                    print("No more data recieved")
                    break
        
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
            
        finally:
            clientsocket.close()
            print("Connection closed")