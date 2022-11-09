from app.api import bp
from flask import jsonify, request, make_response
from app.models import SensorData, VirtualData, InputData
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

@bp.route('/data/sensor', methods=['GET'])
@token_auth.login_required
def get_last_data():
    return jsonify(SensorData.query.order_by(SensorData.datetime.desc()).first().to_dict())

@bp.route('/data/sensor/all', methods=['GET'])
@token_auth.login_required
def get_alldata():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = SensorData.to_collection_dict(SensorData.query, page, per_page, 'api.get_alldata')
    return jsonify(data)

@bp.route('/data/sensor', methods=['POST'])
@token_auth.login_required
def add_data():
    jsondata = request.get_json()
    data=SensorData()
    data.from_dict(jsondata)
    db.session.add(data)
    db.session.commit()    
    response = jsonify(data.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.data', id=data.id)
    return response

@bp.route('/data/virtualdata', methods=['GET'])
@token_auth.login_required
def get_virtualdata():
    return jsonify(VirtualData.query.order_by(VirtualData.id.desc()).first().to_dict())

@bp.route('/data/virtualdata', methods=['POST'])
@token_auth.login_required
def post_virtualdata():
    jsondata = request.get_json()
    virtualdata = VirtualData()
    virtualdata.from_dict(jsondata)
    db.session.add(virtualdata)
    db.session.commit()
    response = jsonify(virtualdata.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.data', id=virtualdata.id)
    return response

@bp.route('/data/inputdata', methods=['GET'])
@token_auth.login_required
def get_inputdata():
    return jsonify(InputData.query.order_by(InputData.id.desc()).first().to_dict())

@bp.route('/data/inputdata', methods=['POST'])
@token_auth.login_required
def post_inputdata():
    jsondata = request.get_json()
    inputdata = InputData()
    inputdata.from_dict(jsondata)
    db.session.add(inputdata)
    db.session.commit()
    response = jsonify(inputdata.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.data', id=inputdata.id)
    return response
