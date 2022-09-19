from app.api import bp
from flask import jsonify, request, make_response
from app.models import Data, FmuData, ValveOpening
from flask import url_for
from app import db
from app.api.errors import bad_request
from app.api.auth import token_auth

def crossdomain(f):
    def wrapped_function(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        h = resp.headers
        h['Access-Control-Allow-Origin'] = '*'
        h['Access-Control-Allow-Methods'] = "GET, OPTIONS, POST"
        h['Access-Control-Max-Age'] = str(21600)
        requested_headers = request.headers.get('Access-Control-Request-Headers')
        if requested_headers:
            h['Access-Control-Allow-Headers'] = requested_headers
        return resp
    return wrapped_function

@bp.route('/data/last', methods=['GET'])
@token_auth.login_required
def get_last_data():
    return jsonify(Data.query.order_by(Data.datetime.desc()).first().to_dict())   

@bp.route('/data/valve', methods=['GET'])
@token_auth.login_required
def get_valve_data():
    valve = ValveOpening.query.order_by(ValveOpening.id.desc()).first().to_dict()   
    valve["valve"] = valve.pop("datetime")
    return valve 

@bp.route('/data/lastchart', methods=['GET'])
@crossdomain
#@token_auth.login_required
def get_last_chartdata():
    data1 = Data.query.order_by(Data.datetime.desc()).first().to_dict()
    data2 = FmuData.query.order_by(FmuData.datetime.desc()).first().to_dict()
    data1.update(data2) 
    return data1

@bp.route('/data/all', methods=['GET'])
@token_auth.login_required
def get_alldata():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Data.to_collection_dict(Data.query, page, per_page, 'api.get_alldata')
    return jsonify(data)

@bp.route('/data', methods=['POST'])
@token_auth.login_required
def add_data():
    jsondata = request.get_json()
    data=Data()
    data.from_dict(jsondata)
    db.session.add(data)
    db.session.commit()    
    response = jsonify(data.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.data', id=data.id)
    return response

@bp.route('/fmu', methods=['POST'])
@token_auth.login_required
def add_fmudata():
    jsondata = request.get_json()
    fmudata = FmuData()
    fmudata.from_dict(jsondata)
    db.session.add(fmudata)
    db.session.commit()
    response = jsonify(fmudata.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.fmu', id=fmudata.id)
    return response
