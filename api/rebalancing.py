from flask import Blueprint, jsonify, request
from models import Vehicle
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import random

bp = Blueprint('rebalancing', __name__, url_prefix='/rebalancing')

@bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    """
    Check real-time vehicle distribution
    ---
    responses:
      200:
        description: A list of vehicles with their current locations
      500:
        description: Internal server error
    """
    try:
        vehicles = Vehicle.query.all()
        return jsonify([{
            'id': v.id,
            'name': v.name,
            'status': v.status,
            'location': v.location
        } for v in vehicles])
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@bp.route('/task', methods=['POST'])
def schedule_rebalancing_task():
    """
    Schedule rebalancing tasks
    ---
    parameters:
      - name: vehicle_id
        in: body
        required: true
        type: integer
      - name: new_location
        in: body
        required: true
        type: string
    responses:
      201:
        description: Rebalancing task scheduled
      400:
        description: Bad request
      404:
        description: Vehicle not found
      500:
        description: Internal server error
    """
    try:
        data = request.json
        if not all(k in data for k in ('vehicle_id', 'new_location')):
            return jsonify({'error': 'Missing required fields'}), 400

        vehicle = Vehicle.query.get(data['vehicle_id'])

        if not vehicle:
            return jsonify({'error': 'Invalid vehicle ID'}), 404

        vehicle.location = data['new_location']

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

        vehicles = Vehicle.query.all()

        # Simulating AI-based optimization suggestions
        suggestions = []
        locations = ['Downtown', 'Suburb', 'Business District', 'Residential Area']
        for vehicle in vehicles:
            optimal_location = random.choice(locations)
            if optimal_location != vehicle.location:
                suggestions.append({
                    'vehicle_id': vehicle.id,
                    'vehicle_name': vehicle.name,
                    'current_location': vehicle.location,
                    'optimal_location': optimal_location,
                    'action': 'Move'
                })

        return jsonify({
            'time_range': time_range,
            'total_vehicles': len(vehicles),
            'optimization_suggestions': suggestions
        })
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
