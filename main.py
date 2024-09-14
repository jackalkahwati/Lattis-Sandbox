from flask import Flask, render_template, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from extensions import db
import os
import logging
from dotenv import load_dotenv
from data_store import data_store

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    CORS(app)  # Enable CORS for all routes

    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate = Migrate(app, db)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')  # Provide a default secret key

    @app.route('/')
    def index():
        app.logger.debug(f"Rendering template: {app.template_folder}/index.html")
        mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
        if not mapbox_access_token:
            app.logger.error("MAPBOX_ACCESS_TOKEN is not set in the environment variables")
        return render_template('index.html', MAPBOX_ACCESS_TOKEN=mapbox_access_token)

    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"404 error: {error}")
        return jsonify({"error": "Not found", "message": str(error)}), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"500 error: {error}")
        return jsonify({"error": "Internal server error", "message": str(error)}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200

    @app.route('/api/config', methods=['GET'])
    def get_api_config():
        api_config = {
            'endpoints': {
                'User Authentication & Authorization': [
                    {'method': 'POST', 'path': '/api/v1/auth/register'},
                    {'method': 'POST', 'path': '/api/v1/auth/login'},
                    {'method': 'POST', 'path': '/api/v1/auth/logout'},
                    {'method': 'GET', 'path': '/api/v1/auth/me'},
                ],
                'Vehicle Management': [
                    {'method': 'GET', 'path': '/api/v1/vehicles'},
                    {'method': 'POST', 'path': '/api/v1/vehicles'},
                    {'method': 'GET', 'path': '/api/v1/vehicles/{id}'},
                    {'method': 'PUT', 'path': '/api/v1/vehicles/{id}'},
                    {'method': 'DELETE', 'path': '/api/v1/vehicles/{id}'},
                ],
                'Fleet Management': [
                    {'method': 'GET', 'path': '/api/v1/fleets'},
                    {'method': 'POST', 'path': '/api/v1/fleets'},
                    {'method': 'GET', 'path': '/api/v1/fleets/{id}'},
                    {'method': 'PUT', 'path': '/api/v1/fleets/{id}'},
                    {'method': 'DELETE', 'path': '/api/v1/fleets/{id}'},
                ],
                'Trip Management': [
                    {'method': 'GET', 'path': '/api/v1/trips'},
                    {'method': 'POST', 'path': '/api/v1/trips'},
                    {'method': 'GET', 'path': '/api/v1/trips/{id}'},
                    {'method': 'PUT', 'path': '/api/v1/trips/{id}'},
                ],
                'Maintenance': [
                    {'method': 'GET', 'path': '/api/v1/maintenance'},
                    {'method': 'POST', 'path': '/api/v1/maintenance'},
                ],
                'Reporting': [
                    {'method': 'GET', 'path': '/api/v1/reports'},
                    {'method': 'POST', 'path': '/api/v1/reports'},
                ],
            }
        }
        return jsonify(api_config)

    @app.route('/api/map', methods=['GET'])
    def get_map_data():
        return jsonify(data_store.get_vehicles())

    # User Authentication & Authorization
    @app.route('/api/v1/auth/register', methods=['POST'])
    def register():
        return jsonify(data_store.register_user(request.json)), 201

    @app.route('/api/v1/auth/login', methods=['POST'])
    def login():
        return jsonify(data_store.login_user(request.json)), 200

    @app.route('/api/v1/auth/logout', methods=['POST'])
    def logout():
        return jsonify(data_store.logout_user()), 200

    @app.route('/api/v1/auth/me', methods=['GET'])
    def get_current_user():
        return jsonify(data_store.get_current_user()), 200

    # Vehicle Management
    @app.route('/api/v1/vehicles', methods=['GET'])
    def get_vehicles():
        return jsonify(data_store.get_vehicles())

    @app.route('/api/v1/vehicles', methods=['POST'])
    def create_vehicle():
        return jsonify(data_store.add_vehicle(request.json)), 201

    @app.route('/api/v1/vehicles/<int:id>', methods=['GET'])
    def get_vehicle(id):
        return jsonify(data_store.get_vehicle(id))

    @app.route('/api/v1/vehicles/<int:id>', methods=['PUT'])
    def update_vehicle(id):
        return jsonify(data_store.update_vehicle(id, request.json))

    @app.route('/api/v1/vehicles/<int:id>', methods=['DELETE'])
    def delete_vehicle(id):
        return jsonify(data_store.delete_vehicle(id))

    # Fleet Management
    @app.route('/api/v1/fleets', methods=['GET'])
    def get_fleets():
        return jsonify(data_store.get_fleets())

    @app.route('/api/v1/fleets', methods=['POST'])
    def create_fleet():
        return jsonify(data_store.add_fleet(request.json)), 201

    @app.route('/api/v1/fleets/<int:id>', methods=['GET'])
    def get_fleet(id):
        return jsonify(data_store.get_fleet(id))

    @app.route('/api/v1/fleets/<int:id>', methods=['PUT'])
    def update_fleet(id):
        return jsonify(data_store.update_fleet(id, request.json))

    @app.route('/api/v1/fleets/<int:id>', methods=['DELETE'])
    def delete_fleet(id):
        return jsonify(data_store.delete_fleet(id))

    # Trip Management
    @app.route('/api/v1/trips', methods=['GET'])
    def get_trips():
        return jsonify(data_store.get_trips())

    @app.route('/api/v1/trips', methods=['POST'])
    def create_trip():
        return jsonify(data_store.add_trip(request.json)), 201

    @app.route('/api/v1/trips/<int:id>', methods=['GET'])
    def get_trip(id):
        return jsonify(data_store.get_trip(id))

    @app.route('/api/v1/trips/<int:id>', methods=['PUT'])
    def update_trip(id):
        return jsonify(data_store.update_trip(id, request.json))

    # Maintenance
    @app.route('/api/v1/maintenance', methods=['GET'])
    def get_maintenance():
        return jsonify(data_store.get_maintenance())

    @app.route('/api/v1/maintenance', methods=['POST'])
    def create_maintenance():
        return jsonify(data_store.add_maintenance(request.json)), 201

    # Reporting
    @app.route('/api/v1/reports', methods=['GET'])
    def get_reports():
        return jsonify(data_store.get_reports())

    @app.route('/api/v1/reports', methods=['POST'])
    def create_report():
        return jsonify(data_store.add_report(request.json)), 201

    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5001, debug=debug_mode)
