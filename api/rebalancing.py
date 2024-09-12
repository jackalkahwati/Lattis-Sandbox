from flask import Blueprint, jsonify
from models import Station

bp = Blueprint('rebalancing', __name__, url_prefix='/rebalancing')

@bp.route('/stations', methods=['GET'])
def get_stations():
    """
    Check real-time bike distribution
    ---
    responses:
      200:
        description: A list of stations with bike distribution
    """
    stations = Station.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'capacity': s.capacity,
        'current_bikes': s.current_bikes
    } for s in stations])
