from flask import Blueprint, jsonify, request
from models import Fleet
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError

bp = Blueprint('fleet', __name__, url_prefix='/api/v1/fleets')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class FleetSchema(Schema):
    name = fields.String(required=True)

@bp.route('', methods=['POST'])
def create_fleet():
    try:
        schema = FleetSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        new_fleet = Fleet(name=data['name'])
        db.session.add(new_fleet)
        db.session.commit()
        return jsonify({"message": "Fleet created successfully", "fleet_id": new_fleet.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_fleet: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while creating the fleet"}), 500

@bp.route('/<int:fleet_id>', methods=['PATCH'])
def update_fleet(fleet_id):
    try:
        schema = FleetSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        fleet = Fleet.query.get(fleet_id)
        if not fleet:
            return jsonify({"error": "Fleet not found"}), 404

        fleet.name = data['name']
        db.session.commit()
        return jsonify({"message": "Fleet updated successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_fleet: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the fleet"}), 500

@bp.route('/<int:fleet_id>', methods=['DELETE'])
def delete_fleet(fleet_id):
    try:
        fleet = Fleet.query.get(fleet_id)
        if not fleet:
            return jsonify({"error": "Fleet not found"}), 404

        db.session.delete(fleet)
        db.session.commit()
        return jsonify({"message": "Fleet deleted successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_fleet: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the fleet"}), 500

@bp.route('/<int:fleet_id>', methods=['GET'])
def get_fleet(fleet_id):
    try:
        fleet = Fleet.query.get(fleet_id)
        if not fleet:
            return jsonify({"error": "Fleet not found"}), 404

        return jsonify({
            "id": fleet.id,
            "name": fleet.name,
            "created_at": fleet.created_at.isoformat()
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_fleet: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the fleet"}), 500

@bp.route('', methods=['GET'])
def list_fleets():
    try:
        fleets = Fleet.query.all()
        return jsonify([{
            "id": fleet.id,
            "name": fleet.name,
            "created_at": fleet.created_at.isoformat()
        } for fleet in fleets]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_fleets: {str(e)}")
        return jsonify({"error": "An error occurred while fetching fleets"}), 500
