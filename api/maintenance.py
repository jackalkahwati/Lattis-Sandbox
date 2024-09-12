from flask import Blueprint, jsonify, request
from models import MaintenanceTask
from extensions import db

bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@bp.route('/schedule', methods=['GET'])
def get_maintenance_schedule():
    """
    View current maintenance schedules
    ---
    responses:
      200:
        description: A list of maintenance tasks
    """
    tasks = MaintenanceTask.query.all()
    return jsonify([{
        'id': t.id,
        'vehicle_id': t.vehicle_id,
        'description': t.description,
        'status': t.status
    } for t in tasks])

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
    """
    data = request.json
    task = MaintenanceTask(
        vehicle_id=data['vehicle_id'],
        description=data['description'],
        status='Pending'
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Maintenance task created', 'id': task.id}), 201
