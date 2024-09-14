from flask import Blueprint, jsonify, request
from models import Report, Vehicle, Trip
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, timedelta

bp = Blueprint('reporting', __name__, url_prefix='/api/v1')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class ReportSchema(Schema):
    title = fields.String(required=True)
    content = fields.Dict(required=True)

@bp.route('/analytics/usage', methods=['GET'])
def get_usage_analytics():
    try:
        # Get usage data for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        trips = Trip.query.filter(Trip.start_time >= thirty_days_ago).all()
        vehicles = Vehicle.query.all()

        total_trips = len(trips)
        total_distance = sum((trip.end_time - trip.start_time).total_seconds() / 3600 for trip in trips if trip.end_time)  # Assuming 1 hour = 1 distance unit
        avg_trip_duration = sum((trip.end_time - trip.start_time).total_seconds() for trip in trips if trip.end_time) / total_trips if total_trips > 0 else 0

        vehicle_usage = {}
        for vehicle in vehicles:
            vehicle_trips = [trip for trip in trips if trip.vehicle_id == vehicle.id]
            vehicle_usage[vehicle.id] = {
                'total_trips': len(vehicle_trips),
                'total_distance': sum((trip.end_time - trip.start_time).total_seconds() / 3600 for trip in vehicle_trips if trip.end_time),
                'utilization_rate': len(vehicle_trips) / total_trips if total_trips > 0 else 0
            }

        usage_data = {
            'total_trips': total_trips,
            'total_distance': total_distance,
            'avg_trip_duration': avg_trip_duration,
            'vehicle_usage': vehicle_usage,
            'period': '30 days'
        }

        return jsonify(usage_data), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_usage_analytics: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching usage analytics'}), 500

@bp.route('/reports', methods=['POST'])
def generate_report():
    try:
        schema = ReportSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        new_report = Report(
            title=data['title'],
            content=str(data['content']),  # Convert dict to string for storage
            created_at=datetime.utcnow()
        )
        db.session.add(new_report)
        db.session.commit()
        return jsonify({"message": "Report generated successfully", "report_id": new_report.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in generate_report: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while generating the report"}), 500

@bp.route('/reports/<int:report_id>', methods=['GET'])
def get_report(report_id):
    try:
        report = Report.query.get(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404

        return jsonify({
            "id": report.id,
            "title": report.title,
            "content": eval(report.content),  # Convert string back to dict
            "created_at": report.created_at.isoformat()
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_report: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the report"}), 500

@bp.route('/reports', methods=['GET'])
def list_reports():
    try:
        reports = Report.query.all()
        return jsonify([{
            "id": report.id,
            "title": report.title,
            "created_at": report.created_at.isoformat()
        } for report in reports]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in list_reports: {str(e)}")
        return jsonify({"error": "An error occurred while fetching reports"}), 500
