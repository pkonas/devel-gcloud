import os
import base64
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, timedelta
from flask import url_for

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

class ValveOpening(PaginatedAPIMixin, db.Model): #InputData
    id = db.Column(db.Integer, primary_key=True)
    valve_value = db.Column(db.Integer)
    
    def to_dict(self):
        data = {
            "datetime" : self.valve_value
        }
        return data

class Data(PaginatedAPIMixin, db.Model): #SensorData
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    pressure1 = db.Column(db.Float)
    pressure2 = db.Column(db.Float)
    flow1 = db.Column(db.Float)
    flow2 = db.Column(db.Float)
    temperature = db.Column(db.Float)
    valve_position = db.Column(db.Float)

    def to_dict(self):
        data = {
            "id" : self.id,
            "datetime" : self.datetime,
            "pressure1" : self.pressure1,
            "pressure2" : self.pressure2,
            "flow1" : self.flow1,
            "flow2" : self.flow2,
            "temperature" : self.temperature,
            "valve_position" : self.valve_position
        }
        return data

    def from_dict(self, data):
        data["datetime"] = datetime.fromisoformat(data["datetime"])
        for field in ['datetime', 'pressure1', 'pressure2', 'flow1', 'flow2', 'temperature', 'valve_position']:
            if field in data:
                setattr(self, field, data[field])

role_user_table = db.Table('role_user',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

class FmuData(PaginatedAPIMixin, db.Model): #VirtualData
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

    def from_dict(self, data):
        data["datetime"] = datetime.fromisoformat(data["datetime"])
        for field in ['datetime', 'Ball_Valve_Pressure_drop', 'Bend_Pressure_drop',
                      'Control_Valve_Static_pressure_diff', 'FlowMonitor1', 'FlowMonitor2',
                      'ManometrMonitor','PressureMonitor1','PressureMonitor2','Pump_pressure_rise']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            "id" : self.id,
            "datetime" : self.datetime,
            "Ball_Valve_Pressure_drop" : self.Ball_Valve_Pressure_drop,
            "Bend_Pressure_drop" : self.Bend_Pressure_drop,
            "Control_Valve_Static_pressure_diff" : self.Control_Valve_Static_pressure_diff,
            "FlowMonitor1" : self.FlowMonitor1,
            "FlowMonitor2" : self.FlowMonitor2,
            "ManometrMonitor" : self.ManometrMonitor,
            "PressureMonitor1" : self.PressureMonitor1,
            "PressureMonitor2" : self.PressureMonitor2,
            "Pump_pressure_rise" : self.Pump_pressure_rise
        }
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
