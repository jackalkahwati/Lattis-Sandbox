from flask import Blueprint, jsonify, request
from models import Vehicle
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError

bp = Blueprint('fleet', __name__, url_prefix='/api/v1/fleet')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class VehicleSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    status = fields.String(required=True)
    location = fields.String(required=True)

@bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    """
    Retrieve all vehicles
    ---
    responses:
      200:
        description: A list of all vehicles
      500:
        description: Internal server error
    """
    try:
        vehicles = Vehicle.query.all()
        vehicle_schema = VehicleSchema(many=True)
        return jsonify(vehicle_schema.dump(vehicles)), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_vehicles: {str(e)}")
        return jsonify({"error": "An error occurred while fetching vehicles"}), 500

@bp.route('/vehicles', methods=['POST'])
def create_vehicle():
    """
    Create a new vehicle
    ---
    parameters:
      - name: vehicle
        in: body
        required: true
        schema:
          $ref: '#/definitions/Vehicle'
    responses:
      201:
        description: Vehicle created successfully
      400:
        description: Invalid input
      500:
        description: Internal server error
    """
    try:
        vehicle_schema = VehicleSchema()
        data = vehicle_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        new_vehicle = Vehicle(**data)
        db.session.add(new_vehicle)
        db.session.commit()
        return jsonify(vehicle_schema.dump(new_vehicle)), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_vehicle: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while creating the vehicle"}), 500

# Keep any other existing routes in the file
