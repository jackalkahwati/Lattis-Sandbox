from flask import Blueprint, jsonify, request
from models import User
from extensions import db
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

# The activity logging functionality has been removed as we don't have an ActivityLog model
# If you want to implement this feature in the future, you'll need to create an ActivityLog model
# and update this file accordingly

@bp.route('/', methods=['GET'])
def get_users():
    """
    Get all users
    ---
    responses:
      200:
        description: A list of all users
      500:
        description: Internal server error
    """
    try:
        users = User.query.all()
        return jsonify([{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'created_at': u.created_at.isoformat()
        } for u in users])
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get a specific user
    ---
    parameters:
      - name: user_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: User details
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        })
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
