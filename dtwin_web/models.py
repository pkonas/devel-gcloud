# -*- coding: utf-8 -*-
from dtwin_web import db

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.Float)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)