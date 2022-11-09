import os
import base64
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta
from flask import url_for

class InputData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valve_value = db.Column(db.Integer)
    
    def to_dict(self):
        data = {k:v for k, v in InputData.__dict__.items() if not k.startswith('__')}
        return data

    def from_dict(self, data):
        attributes = [key for key in InputData.__dict__.keys() if not key.startswith('__')]
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    pressure1 = db.Column(db.Float)
    pressure2 = db.Column(db.Float)
    flow1 = db.Column(db.Float)
    flow2 = db.Column(db.Float)
    temperature = db.Column(db.Float)
    valve_position = db.Column(db.Float)

    def to_dict(self):
        data = {k:v for k, v in Data.__dict__.items() if not k.startswith('__')}
        return data

    def from_dict(self, data):
        attributes = self.names()
        data["datetime"] = datetime.fromisoformat(data["datetime"])
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])
                
    def names(self):
        return [key for key in Data.__dict__.keys() if not key.startswith('__')]

role_user_table = db.Table('role_user',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

class VirtualData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    Ball_Valve_Pressure_drop = db.Column(db.Float)
    Bend_Pressure_drop = db.Column(db.Float)
    Control_Valve_Static_pressure_diff = db.Column(db.Float)
    Pump_pressure_rise = db.Column(db.Float)
    ManometrMonitor = db.Column(db.Float)
    FlowMonitor1 = db.Column(db.Float)
    FlowMonitor2 = db.Column(db.Float)
    PressureMonitor1 = db.Column(db.Float)
    PressureMonitor2 = db.Column(db.Float)

    @classmethod
    def _names(cls):
        return [key for key in cls.__dict__.keys() if not key.startswith('__')]

    def _to_dict(self):
        data = {k:v for k, v in VirtualData.__dict__.items() if not k.startswith('__')}
        return data

    def _from_dict(self, data):
        attributes = [key for key in VirtualData.__dict__.keys() if not key.startswith('__') or not key.startswith('_')]
        data["datetime"] = datetime.fromisoformat(data["datetime"])
        for field in attributes:
            if field in data:
                setattr(self, field, data[field])
        return data

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean())
    role = db.relationship('Role', secondary=role_user_table,
    backref='user', lazy=True)

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_role(self, rolename):
        role = Role.query.filter(Role.name==rolename).first()
        db.session.execute(role_user_table.insert(),params={"user_id": self.id, "role_id": role.id},) 
        db.session.commit()

    def is_admin(self):
        rolename = self.role[0].name
        if rolename == "admin":
            return True
        else:
            return False   

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
