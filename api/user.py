from flask import Blueprint, jsonify, request
from models import User, ActivityLog, db
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
    """
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if data['action'] == 'grant':
        user.role = data['role']
    elif data['action'] == 'revoke':
        user.role = 'user'
    else:
        return jsonify({'error': 'Invalid action'}), 400

    db.session.commit()
    return jsonify({'message': f"Access {data['action']}ed for {user.username}"})

@bp.route('/activity', methods=['GET'])
def get_user_activity():
    """
    View logs of user activities
    ---
    responses:
      200:
        description: A list of user activities
    """
    activities = ActivityLog.query.all()
    return jsonify([{
        'id': a.id,
        'user_id': a.user_id,
        'action': a.action,
        'timestamp': a.timestamp.isoformat()
    } for a in activities])
