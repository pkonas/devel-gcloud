from flask import Blueprint
from app.models import ValveOpening

bp = Blueprint('main', __name__)
valve_opening = ValveOpening()

from app.main import routes, adminview
