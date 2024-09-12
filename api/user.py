from flask import Blueprint, jsonify, request
from models import User, ActivityLog, db
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/access', methods=['POST'])
def manage_access():
    """
    Grant or revoke access based on roles
    ---
    parameters:
      - name: username
        in: body
        required: true
        type: string
      - name: role
        in: body
        required: true
        type: string
      - name: action
        in: body
        required: true
        type: string
        enum: [grant, revoke]
    responses:
      200:
        description: Access updated
      400:
        description: Bad request
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        data = request.json
        if not all(k in data for k in ('username', 'role', 'action')):
            return jsonify({'error': 'Missing required fields'}), 400

        if data['action'] not in ['grant', 'revoke']:
            return jsonify({'error': 'Invalid action'}), 400

        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if data['action'] == 'grant':
            user.role = data['role']
        elif data['action'] == 'revoke':
            user.role = 'user'

        db.session.commit()
        return jsonify({'message': f"Access {data['action']}ed for {user.username}"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@bp.route('/activity', methods=['GET'])
def get_user_activity():
    """
    View logs of user activities
    ---
    responses:
      200:
        description: A list of user activities
      500:
        description: Internal server error
    """
    try:
        activities = ActivityLog.query.all()
        return jsonify([{
            'id': a.id,
            'user_id': a.user_id,
            'action': a.action,
            'timestamp': a.timestamp.isoformat()
        } for a in activities])
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
