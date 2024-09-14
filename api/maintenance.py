from flask import Blueprint, jsonify, request
from models import Maintenance, Vehicle, Alert
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

bp = Blueprint('maintenance', __name__, url_prefix='/api/v1')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class MaintenanceSchema(Schema):
    vehicle_id = fields.Integer(required=True)
    description = fields.String(required=True)
    scheduled_date = fields.DateTime(required=True)

class MaintenanceUpdateSchema(Schema):
    status = fields.String(required=True)

class AlertSchema(Schema):
    vehicle_id = fields.Integer(required=True)
    message = fields.String(required=True)

@bp.route('/maintenance', methods=['POST'])
def schedule_maintenance():
    try:
        schema = MaintenanceSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        new_maintenance = Maintenance(
            vehicle_id=data['vehicle_id'],
            description=data['description'],
            scheduled_date=data['scheduled_date'],
            status='Scheduled'
        )
        db.session.add(new_maintenance)
        db.session.commit()
        return jsonify({"message": "Maintenance task scheduled successfully", "maintenance_id": new_maintenance.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in schedule_maintenance: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while scheduling the maintenance task"}), 500

@bp.route('/maintenance/<int:maintenance_id>', methods=['PATCH'])
def update_maintenance(maintenance_id):
    try:
        schema = MaintenanceUpdateSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        maintenance = Maintenance.query.get(maintenance_id)
        if not maintenance:
            return jsonify({"error": "Maintenance task not found"}), 404

        maintenance.status = data['status']
        db.session.commit()
        return jsonify({"message": "Maintenance task updated successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_maintenance: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the maintenance task"}), 500

@bp.route('/vehicles/<int:vehicle_id>/maintenance', methods=['GET'])
def get_vehicle_maintenance(vehicle_id):
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        maintenance_tasks = Maintenance.query.filter_by(vehicle_id=vehicle_id).all()
        return jsonify([{
            "id": task.id,
            "description": task.description,
            "scheduled_date": task.scheduled_date.isoformat(),
            "status": task.status,
            "created_at": task.created_at.isoformat()
        } for task in maintenance_tasks]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_vehicle_maintenance: {str(e)}")
        return jsonify({"error": "An error occurred while fetching maintenance tasks"}), 500

@bp.route('/maintenance', methods=['GET'])
def list_maintenance():
    try:
        maintenance_tasks = Maintenance.query.all()
        return jsonify([{
            "id": task.id,
            "vehicle_id": task.vehicle_id,
            "description": task.description,
            "scheduled_date": task.scheduled_date.isoformat(),
            "status": task.status,
            "created_at": task.created_at.isoformat()
        } for task in maintenance_tasks]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_maintenance: {str(e)}")
        return jsonify({"error": "An error occurred while fetching maintenance tasks"}), 500

@bp.route('/alerts', methods=['POST'])
def create_alert():
    try:
        schema = AlertSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        new_alert = Alert(
            vehicle_id=data['vehicle_id'],
            message=data['message'],
            created_at=datetime.utcnow()
        )
        db.session.add(new_alert)
        db.session.commit()
        return jsonify({"message": "Alert created successfully", "alert_id": new_alert.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_alert: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while creating the alert"}), 500

@bp.route('/alerts', methods=['GET'])
def list_alerts():
    try:
        alerts = Alert.query.filter_by(resolved_at=None).all()
        return jsonify([{
            "id": alert.id,
            "vehicle_id": alert.vehicle_id,
            "message": alert.message,
            "created_at": alert.created_at.isoformat()
        } for alert in alerts]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_alerts: {str(e)}")
        return jsonify({"error": "An error occurred while fetching alerts"}), 500
