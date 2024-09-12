from flask import Blueprint, jsonify, request
from models import Vehicle, MaintenanceTask
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging

bp = Blueprint('fleet', __name__, url_prefix='/fleet')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

@bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    """
    Retrieve real-time vehicle data
    ---
    responses:
      200:
        description: A list of vehicles
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
        logger.error(f"Database error in get_vehicles: {str(e)}")
        return jsonify({'error': 'A database error occurred. Please try again later or contact support.'}), 500

@bp.route('/task', methods=['POST'])
def assign_task():
    """
    Assigns maintenance or rebalancing tasks
    ---
    parameters:
      - name: vehicle_id
        in: body
        required: true
        type: integer
      - name: task_type
        in: body
        required: true
        type: string
      - name: description
        in: body
        required: true
        type: string
    responses:
      201:
        description: Task assigned successfully
      400:
        description: Bad request
      404:
        description: Vehicle not found
      500:
        description: Internal server error
    """
    try:
        data = request.json
        if not all(k in data for k in ('vehicle_id', 'task_type', 'description')):
            return jsonify({'error': 'Missing required fields'}), 400

        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404

        task = MaintenanceTask(
            vehicle_id=data['vehicle_id'],
            description=data['description'],
            status='Pending'
        )
        db.session.add(task)
        db.session.commit()

        return jsonify({'message': 'Task assigned successfully', 'task_id': task.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in assign_task: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'A database error occurred. Please try again later or contact support.'}), 500

@bp.route('/status', methods=['GET'])
def get_fleet_status():
    """
    Monitors vehicle statuses (live, out of service, etc.)
    ---
    responses:
      200:
        description: Fleet status
      500:
        description: Internal server error
    """
    try:
        vehicles = Vehicle.query.all()
        status_count = {
            'live': 0,
            'out_of_service': 0,
            'maintenance': 0
        }
        for vehicle in vehicles:
            if vehicle.status in status_count:
                status_count[vehicle.status] += 1
            else:
                status_count[vehicle.status] = 1

        return jsonify({
            'total_vehicles': len(vehicles),
            'status_breakdown': status_count
        })
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_fleet_status: {str(e)}")
        return jsonify({'error': 'A database error occurred. Please try again later or contact support.'}), 500
