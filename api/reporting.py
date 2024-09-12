from flask import Blueprint, jsonify
from models import Report, MaintenanceTask
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

bp = Blueprint('reporting', __name__, url_prefix='/reports')

@bp.route('/usage', methods=['GET'])
def get_usage_report():
    """
    Retrieve fleet usage data
    ---
    responses:
      200:
        description: Fleet usage report
      404:
        description: No usage report available
      500:
        description: Internal server error
    """
    try:
        report = Report.query.filter_by(type='usage').order_by(Report.created_at.desc()).first()
        if report:
            return jsonify({
                'id': report.id,
                'type': report.type,
                'data': report.data,
                'created_at': report.created_at.isoformat()
            })
        else:
            return jsonify({'error': 'No usage report available'}), 404
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@bp.route('/maintenance', methods=['GET'])
def get_maintenance_report():
    """
    Analyze maintenance actions and downtime
    ---
    responses:
      200:
        description: Maintenance report with actions and downtime analysis
      500:
        description: Internal server error
    """
    try:
        # Get maintenance tasks for the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        tasks = MaintenanceTask.query.filter(MaintenanceTask.created_at >= thirty_days_ago).all()

        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.status == 'Completed')
        pending_tasks = sum(1 for task in tasks if task.status == 'Pending')
        in_progress_tasks = total_tasks - completed_tasks - pending_tasks

        # Calculate average downtime (assuming each task takes 2 hours on average)
        total_downtime = sum(2 for task in tasks if task.status == 'Completed')
        avg_downtime = total_downtime / completed_tasks if completed_tasks > 0 else 0

        report_data = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'average_downtime_hours': round(avg_downtime, 2),
            'total_downtime_hours': total_downtime,
            'period': '30 days'
        }

        return jsonify(report_data)
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
