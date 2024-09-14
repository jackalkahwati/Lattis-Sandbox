from flask import Blueprint, jsonify, request
from models import Trip, Vehicle
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

bp = Blueprint('trip', __name__, url_prefix='/api/v1/trips')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class TripSchema(Schema):
    vehicle_id = fields.Integer(required=True)
    start_location = fields.String(required=True)
    end_location = fields.String(required=False)

class EndTripSchema(Schema):
    end_location = fields.String(required=True)

@bp.route('', methods=['POST'])
def start_trip():
    try:
        schema = TripSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({"error": "Vehicle not found"}), 404

        new_trip = Trip(
            vehicle_id=data['vehicle_id'],
            start_location=data['start_location'],
            start_time=datetime.utcnow()
        )
        db.session.add(new_trip)
        db.session.commit()
        return jsonify({"message": "Trip started successfully", "trip_id": new_trip.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in start_trip: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while starting the trip"}), 500

@bp.route('/<int:trip_id>', methods=['PATCH'])
def end_trip(trip_id):
    try:
        schema = EndTripSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        trip = Trip.query.get(trip_id)
        if not trip:
            return jsonify({"error": "Trip not found"}), 404

        if trip.end_time:
            return jsonify({"error": "Trip has already ended"}), 400

        trip.end_location = data['end_location']
        trip.end_time = datetime.utcnow()
        db.session.commit()
        return jsonify({"message": "Trip ended successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in end_trip: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while ending the trip"}), 500

@bp.route('/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    try:
        trip = Trip.query.get(trip_id)
        if not trip:
            return jsonify({"error": "Trip not found"}), 404

        return jsonify({
            "id": trip.id,
            "vehicle_id": trip.vehicle_id,
            "start_location": trip.start_location,
            "end_location": trip.end_location,
            "start_time": trip.start_time.isoformat(),
            "end_time": trip.end_time.isoformat() if trip.end_time else None
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_trip: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the trip"}), 500

@bp.route('', methods=['GET'])
def list_trips():
    try:
        trips = Trip.query.all()
        return jsonify([{
            "id": trip.id,
            "vehicle_id": trip.vehicle_id,
            "start_location": trip.start_location,
            "end_location": trip.end_location,
            "start_time": trip.start_time.isoformat(),
            "end_time": trip.end_time.isoformat() if trip.end_time else None
        } for trip in trips]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_trips: {str(e)}")
        return jsonify({"error": "An error occurred while fetching trips"}), 500