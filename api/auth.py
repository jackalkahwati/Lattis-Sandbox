from flask import Blueprint, jsonify, request
from models import User, Role
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from marshmallow import Schema, fields, ValidationError
import secrets

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class UserSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.Email(required=True)
    role = fields.String(required=False)

class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

class RoleSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()

@bp.route('/register', methods=['POST'])
def register():
    try:
        schema = UserSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])
        if 'role' in data:
            role = Role.query.filter_by(name=data['role']).first()
            if not role:
                return jsonify({"error": "Invalid role"}), 400
            new_user.role = role
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in register: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while registering the user"}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        schema = LoginSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            # In a real application, you would generate and return a token here
            return jsonify({"message": "User logged in successfully", "user_id": user.id, "role": user.role.name if user.role else None}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in login: {str(e)}")
        return jsonify({"error": "An error occurred while logging in"}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    # In a real application, you would invalidate the user's token here
    return jsonify({"message": "User logged out successfully"}), 200

@bp.route('/me', methods=['GET'])
def get_current_user():
    # In a real application, you would get the user from the token
    # For this example, we'll just return a mock user
    try:
        user = {
            "id": 1,
            "username": "testuser",
            "email": "testuser@example.com",
            "role": "user"
        }
        return jsonify(user), 200
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        return jsonify({"error": "An error occurred while fetching user details"}), 500

@bp.route('/roles', methods=['GET'])
def get_roles():
    try:
        roles = Role.query.all()
        return jsonify([{"id": role.id, "name": role.name, "description": role.description} for role in roles]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_roles: {str(e)}")
        return jsonify({"error": "An error occurred while fetching roles"}), 500

@bp.route('/roles', methods=['POST'])
def create_role():
    try:
        schema = RoleSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        new_role = Role(name=data['name'], description=data.get('description'))
        db.session.add(new_role)
        db.session.commit()
        return jsonify({"message": "Role created successfully", "role_id": new_role.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in create_role: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while creating the role"}), 500

@bp.route('/roles/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    try:
        schema = RoleSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({"error": "Role not found"}), 404
        role.name = data['name']
        role.description = data.get('description', role.description)
        db.session.commit()
        return jsonify({"message": "Role updated successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in update_role: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the role"}), 500

@bp.route('/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({"error": "Role not found"}), 404
        db.session.delete(role)
        db.session.commit()
        return jsonify({"message": "Role deleted successfully"}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in delete_role: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the role"}), 500

@bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['POST', 'DELETE'])
def manage_user_role(user_id, role_id):
    try:
        user = User.query.get(user_id)
        role = Role.query.get(role_id)
        if not user or not role:
            return jsonify({"error": "User or role not found"}), 404

        if request.method == 'POST':
            user.role = role
            message = "Role assigned to user successfully"
        else:  # DELETE
            user.role = None
            message = "Role removed from user successfully"

        db.session.commit()
        return jsonify({"message": message}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in manage_user_role: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while managing user role"}), 500
