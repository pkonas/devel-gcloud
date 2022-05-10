# -*- coding: utf-8 -*-
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
import socket
import struct
from app.models import Data
from app import create_app

#vytvory novu app webu pre workera
app = create_app()

app.app_context().push()

#vytvorí server na TCP komunikáciu s clientom
def start_server():
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
                    print(f"Data recieved: {data[0]}")
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
