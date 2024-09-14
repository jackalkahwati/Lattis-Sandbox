from flask import Blueprint, jsonify, request
from models import Vehicle
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError

bp = Blueprint('vehicle', __name__, url_prefix='/api/v1/vehicles')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class VehicleSchema(Schema):
    name = fields.String(required=True)
    status = fields.String(required=True)
    location = fields.String(required=True)

@bp.route('', methods=['POST'])
def create_vehicle():
    try:
        schema = VehicleSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        new_vehicle = Vehicle(**data)
        db.session.add(new_vehicle)
        db.session.commit()
        return jsonify({"message": "Vehicle created successfully", "vehicle_id": new_vehicle.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_vehicle: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while creating the vehicle"}), 500

@bp.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        return jsonify({
            "id": vehicle.id,
            "name": vehicle.name,
            "status": vehicle.status,
            "location": vehicle.location,
            "created_at": vehicle.created_at.isoformat()
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_vehicle: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the vehicle"}), 500

@bp.route('/<int:vehicle_id>', methods=['PATCH'])
def update_vehicle(vehicle_id):
    try:
        schema = VehicleSchema(partial=True)
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        for key, value in data.items():
            setattr(vehicle, key, value)

        db.session.commit()
        return jsonify({"message": "Vehicle updated successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_vehicle: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the vehicle"}), 500

@bp.route('/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        db.session.delete(vehicle)
        db.session.commit()
        return jsonify({"message": "Vehicle deleted successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_vehicle: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the vehicle"}), 500

@bp.route('', methods=['GET'])
def list_vehicles():
    try:
        vehicles = Vehicle.query.all()
        return jsonify([{
            "id": v.id,
            "name": v.name,
            "status": v.status,
            "location": v.location,
            "created_at": v.created_at.isoformat()
        } for v in vehicles]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_vehicles: {str(e)}")
        return jsonify({"error": "An error occurred while fetching vehicles"}), 500