from flask import Blueprint, jsonify, request
from models import Geofence
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError
import json

bp = Blueprint('geofencing', __name__, url_prefix='/api/v1/geofences')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class GeofenceSchema(Schema):
    name = fields.String(required=True)
    coordinates = fields.String(required=True)  # JSON string of coordinates

@bp.route('', methods=['POST'])
def create_geofence():
    try:
        schema = GeofenceSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        # Validate coordinates JSON
        json.loads(data['coordinates'])
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid coordinates format"}), 400

    try:
        new_geofence = Geofence(
            name=data['name'],
            coordinates=data['coordinates']
        )
        db.session.add(new_geofence)
        db.session.commit()
        return jsonify({"message": "Geofence created successfully", "geofence_id": new_geofence.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_geofence: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while creating the geofence"}), 500

@bp.route('/<int:geofence_id>', methods=['PATCH'])
def update_geofence(geofence_id):
    try:
        schema = GeofenceSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        geofence = Geofence.query.get(geofence_id)
        if not geofence:
            return jsonify({"error": "Geofence not found"}), 404

        # Validate coordinates JSON if provided
        if 'coordinates' in data:
            try:
                json.loads(data['coordinates'])
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid coordinates format"}), 400

        for key, value in data.items():
            setattr(geofence, key, value)

        db.session.commit()
        return jsonify({"message": "Geofence updated successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_geofence: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the geofence"}), 500

@bp.route('/<int:geofence_id>', methods=['DELETE'])
def delete_geofence(geofence_id):
    try:
        geofence = Geofence.query.get(geofence_id)
        if not geofence:
            return jsonify({"error": "Geofence not found"}), 404

        db.session.delete(geofence)
        db.session.commit()
        return jsonify({"message": "Geofence deleted successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_geofence: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the geofence"}), 500

@bp.route('/<int:geofence_id>', methods=['GET'])
def get_geofence(geofence_id):
    try:
        geofence = Geofence.query.get(geofence_id)
        if not geofence:
            return jsonify({"error": "Geofence not found"}), 404

        return jsonify({
            "id": geofence.id,
            "name": geofence.name,
            "coordinates": json.loads(geofence.coordinates),
            "created_at": geofence.created_at.isoformat()
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_geofence: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the geofence"}), 500

@bp.route('', methods=['GET'])
def list_geofences():
    try:
        geofences = Geofence.query.all()
        return jsonify([{
            "id": g.id,
            "name": g.name,
            "coordinates": json.loads(g.coordinates),
            "created_at": g.created_at.isoformat()
        } for g in geofences]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_geofences: {str(e)}")
        return jsonify({"error": "An error occurred while fetching geofences"}), 500