from flask import Blueprint, jsonify, request
from models import MaintenanceTask, Vehicle
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import random
from datetime import datetime, timedelta
import logging
from marshmallow import Schema, fields, ValidationError

bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class MaintenanceTaskSchema(Schema):
    vehicle_id = fields.Integer(required=True)
    description = fields.String(required=True)

@bp.route('/schedule', methods=['GET'])
def get_maintenance_schedule():
    """
    View current maintenance schedules
    ---
    responses:
      200:
        description: A list of maintenance tasks
      500:
        description: Internal server error
    """
    try:
        tasks = MaintenanceTask.query.all()
        return jsonify([{
            'id': t.id,
            'vehicle_id': t.vehicle_id,
            'description': t.description,
            'status': t.status,
            'created_at': t.created_at.isoformat()
        } for t in tasks])
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_maintenance_schedule: {str(e)}")
        return jsonify({'error': 'A database error occurred. Please try again later or contact support.'}), 500

@bp.route('/task', methods=['POST'])
def create_maintenance_task():
    """
    Create tasks for repairs
    ---
    parameters:
      - name: vehicle_id
        in: body
        required: true
        type: integer
      - name: description
        in: body
        required: true
        type: string
    responses:
      201:
        description: Maintenance task created
      400:
        description: Bad request
      404:
        description: Vehicle not found
      500:
        description: Internal server error
    """
    try:
        schema = MaintenanceTaskSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({'error': 'Invalid input', 'details': err.messages}), 400

        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({'error': 'Vehicle not found', 'details': f"No vehicle with id {data['vehicle_id']}"}), 404

        task = MaintenanceTask(
            vehicle_id=data['vehicle_id'],
            description=data['description'],
            status='Pending'
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({'message': 'Maintenance task created', 'id': task.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_maintenance_task: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'A database error occurred. Please try again later or contact support.'}), 500

@bp.route('/predictive-maintenance', methods=['GET'])
def get_predictive_maintenance():
    """
    Retrieve predictive maintenance data based on sensor inputs
    ---
    responses:
      200:
        description: Predictive maintenance data for all vehicles
      500:
        description: Internal server error
    """
    try:
        vehicles = Vehicle.query.all()
        predictive_data = []

        for vehicle in vehicles:
            # Simulating sensor data and predictive analysis
            battery_health = random.uniform(0.7, 1.0)
            tire_wear = random.uniform(0, 0.3)
            next_service_date = (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')

            predictive_data.append({
                'vehicle_id': vehicle.id,
                'battery_health': round(battery_health, 2),
                'tire_wear': round(tire_wear, 2),
                'next_service_date': next_service_date,
                'maintenance_priority': 'High' if battery_health < 0.8 or tire_wear > 0.2 else 'Low'
            })

        return jsonify(predictive_data)
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_predictive_maintenance: {str(e)}")
        return jsonify({'error': 'A database error occurred. Please try again later or contact support.'}), 500
