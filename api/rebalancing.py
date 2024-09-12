from flask import Blueprint, jsonify, request
from models import Station, Vehicle
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import random  # For simulating AI-based optimization suggestions

bp = Blueprint('rebalancing', __name__, url_prefix='/rebalancing')

@bp.route('/stations', methods=['GET'])
def get_stations():
    """
    Check real-time bike distribution
    ---
    responses:
      200:
        description: A list of stations with bike distribution
      500:
        description: Internal server error
    """
    try:
        stations = Station.query.all()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'capacity': s.capacity,
            'current_bikes': s.current_bikes
        } for s in stations])
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@bp.route('/task', methods=['POST'])
def schedule_rebalancing_task():
    """
    Schedule rebalancing tasks
    ---
    parameters:
      - name: from_station_id
        in: body
        required: true
        type: integer
      - name: to_station_id
        in: body
        required: true
        type: integer
      - name: num_bikes
        in: body
        required: true
        type: integer
    responses:
      201:
        description: Rebalancing task scheduled
      400:
        description: Bad request
      404:
        description: Station not found
      500:
        description: Internal server error
    """
    try:
        data = request.json
        if not all(k in data for k in ('from_station_id', 'to_station_id', 'num_bikes')):
            return jsonify({'error': 'Missing required fields'}), 400

        from_station = Station.query.get(data['from_station_id'])
        to_station = Station.query.get(data['to_station_id'])

        if not from_station or not to_station:
            return jsonify({'error': 'Invalid station ID'}), 404

        if from_station.current_bikes < data['num_bikes']:
            return jsonify({'error': 'Not enough bikes at the source station'}), 400

        from_station.current_bikes -= data['num_bikes']
        to_station.current_bikes += data['num_bikes']

        db.session.commit()

        return jsonify({'message': 'Rebalancing task scheduled successfully'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@bp.route('/optimization/suggestions', methods=['POST'])
def generate_optimization_suggestions():
    """
    Generate AI-based optimization suggestions for vehicle placement
    ---
    parameters:
      - name: time_range
        in: body
        required: true
        type: string
        enum: [morning, afternoon, evening, night]
    responses:
      200:
        description: Optimization suggestions for vehicle placement
      400:
        description: Bad request
      500:
        description: Internal server error
    """
    try:
        data = request.json
        if 'time_range' not in data or data['time_range'] not in ['morning', 'afternoon', 'evening', 'night']:
            return jsonify({'error': 'Invalid or missing time_range'}), 400

        time_range = data['time_range']

        stations = Station.query.all()
        vehicles = Vehicle.query.all()

        # Simulating AI-based optimization suggestions
        suggestions = []
        for station in stations:
            optimal_bikes = random.randint(max(0, station.capacity - 5), station.capacity)
            diff = optimal_bikes - station.current_bikes

            if diff != 0:
                suggestions.append({
                    'station_id': station.id,
                    'station_name': station.name,
                    'current_bikes': station.current_bikes,
                    'optimal_bikes': optimal_bikes,
                    'action': 'Add' if diff > 0 else 'Remove',
                    'num_bikes': abs(diff)
                })

        return jsonify({
            'time_range': time_range,
            'total_stations': len(stations),
            'total_vehicles': len(vehicles),
            'optimization_suggestions': suggestions
        })
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
