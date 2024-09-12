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

class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)

class RoleSchema(Schema):
    name = fields.String(required=True)
    description = fields.String()

def generate_test_token():
    return secrets.token_urlsafe(32)

@bp.route('/generate-test-token', methods=['POST'])
def create_test_token():
    """
    Generate a test API Access Token
    ---
    responses:
      200:
        description: Test token generated successfully
      500:
        description: Internal server error
    """
    try:
        test_token = generate_test_token()
        return jsonify({"test_token": test_token}), 200
    except Exception as e:
        logger.error(f"Error in create_test_token: {str(e)}")
        return jsonify({"error": "An error occurred while generating the test token"}), 500

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    parameters:
      - name: user
        in: body
        required: true
        schema:
          $ref: '#/definitions/User'
    responses:
      201:
        description: User registered successfully
      400:
        description: Invalid input
      500:
        description: Internal server error
    """
    try:
        schema = UserSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
    except SQLAlchemyError as e:
        logger.error(f"Database error in register: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while registering the user"}), 500

@bp.route('/login', methods=['POST'])
def login():
    """
    Login a user
    ---
    parameters:
      - name: credentials
        in: body
        required: true
        schema:
          $ref: '#/definitions/Login'
    responses:
      200:
        description: User logged in successfully
      400:
        description: Invalid credentials
      500:
        description: Internal server error
    """
    try:
        schema = LoginSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    try:
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            # In a real application, you would generate and return a token here
            return jsonify({"message": "User logged in successfully", "user_id": user.id}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 400
    except SQLAlchemyError as e:
        logger.error(f"Database error in login: {str(e)}")
        return jsonify({"error": "An error occurred while logging in"}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout a user
    ---
    responses:
      200:
        description: User logged out successfully
      500:
        description: Internal server error
    """
    # In a real application, you would invalidate the user's token here
    return jsonify({"message": "User logged out successfully"}), 200

@bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get details of the currently logged-in user
    ---
    responses:
      200:
        description: Current user details
      401:
        description: Unauthorized
      500:
        description: Internal server error
    """
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
    """
    Retrieve the list of user roles
    ---
    responses:
      200:
        description: List of user roles
      500:
        description: Internal server error
    """
    try:
        roles = Role.query.all()
        return jsonify([{"id": role.id, "name": role.name, "description": role.description} for role in roles]), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_roles: {str(e)}")
        return jsonify({"error": "An error occurred while fetching roles"}), 500

@bp.route('/roles', methods=['POST'])
def create_role():
    """
    Create a new user role
    ---
    parameters:
      - name: role
        in: body
        required: true
        schema:
          $ref: '#/definitions/Role'
    responses:
      201:
        description: Role created successfully
      400:
        description: Invalid input
      500:
        description: Internal server error
    """
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

# Add more endpoints for updating and deleting roles, and assigning/removing roles from users
