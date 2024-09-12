from flask import Blueprint, jsonify
from models import Report

bp = Blueprint('reporting', __name__, url_prefix='/reports')

@bp.route('/usage', methods=['GET'])
def get_usage_report():
    """
    Retrieve fleet usage data
    ---
    responses:
      200:
        description: Fleet usage report
    """
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
