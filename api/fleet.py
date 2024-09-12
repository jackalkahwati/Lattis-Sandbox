from flask import Blueprint, jsonify
from models import Vehicle

bp = Blueprint('fleet', __name__, url_prefix='/fleet')

@bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    """
    Retrieve real-time vehicle data
    ---
    responses:
      200:
        description: A list of vehicles
    """
    vehicles = Vehicle.query.all()
    return jsonify([{
        'id': v.id,
        'name': v.name,
        'status': v.status,
        'location': v.location
    } for v in vehicles])
