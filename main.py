from flask import Flask, render_template, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from extensions import db
from api import fleet, maintenance, rebalancing, user, reporting, integration, future_modules, auth, vehicle, trip, payment, geofencing, pricing
import os
import logging
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

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

    # Register blueprints
    app.register_blueprint(fleet.bp)
    app.register_blueprint(maintenance.bp)
    app.register_blueprint(rebalancing.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(reporting.bp)
    app.register_blueprint(integration.bp)
    app.register_blueprint(future_modules.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(vehicle.bp)
    app.register_blueprint(trip.bp)
    app.register_blueprint(payment.bp)
    app.register_blueprint(geofencing.bp)
    app.register_blueprint(pricing.bp)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    csrf = CSRFProtect(app)

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

    # Left Panel (Input/Configuration Panel)
    @app.route('/api/config', methods=['GET'])
    def get_api_config():
        api_config = {
            'searchTypes': ['Vehicle Search', 'Fleet Search', 'Trip Search', 'User Search'],
            'endpoints': {
                'Vehicle Management': [
                    {'method': 'GET', 'path': '/api/v1/vehicles'},
                    {'method': 'PATCH', 'path': '/api/v1/vehicles/{vehicleId}'}
                ],
                'Fleet Management': [
                    {'method': 'POST', 'path': '/api/v1/fleets'},
                    {'method': 'GET', 'path': '/api/v1/fleets/{fleetId}'}
                ],
                'User Management': [
                    {'method': 'GET', 'path': '/api/v1/auth/me'},
                    {'method': 'POST', 'path': '/api/v1/auth/register'},
                    {'method': 'POST', 'path': '/api/v1/users/{userId}/roles/{roleId}'}
                ],
                'Trip Management': [
                    {'method': 'GET', 'path': '/api/v1/trips'},
                    {'method': 'POST', 'path': '/api/v1/trips'}
                ],
                'Pricing Management': [
                    {'method': 'POST', 'path': '/api/v1/pricing/base'},
                    {'method': 'POST', 'path': '/api/v1/pricing/surge'}
                ]
            },
            'exampleQueries': {
                'Vehicle Search': {'method': 'GET', 'path': '/api/v1/vehicles'},
                'Fleet Search': {'method': 'GET', 'path': '/api/v1/fleets'},
                'Trip Search': {'method': 'GET', 'path': '/api/v1/trips'},
                'User Search': {'method': 'GET', 'path': '/api/v1/auth/me'}
            }
        }
        return jsonify(api_config)

    # Central Section (Interactive Map Display)
    @app.route('/api/map', methods=['GET'])
    def get_map_data():
        # Fetch vehicle or fleet data from the database or API
        # and return it as JSON
        vehicles = [
            {'id': 1, 'lat': 40.7128, 'lng': -74.0060, 'status': 'active'},
            {'id': 2, 'lat': 40.7142, 'lng': -74.0094, 'status': 'maintenance'},
            # ... more vehicles
        ]
        return jsonify(vehicles)

    # Right Panel (Query Information & Response Display)
    @app.route('/api/query', methods=['POST'])
    def execute_query():
        # Get the request data
        data = request.get_json()
        endpoint = data.get('endpoint')
        params = data.get('params', {})
        headers = data.get('headers', {})

        # Execute the API request
        response = make_api_request(endpoint, params, headers)

        return jsonify(response)

    # Helper function to make API requests
    def make_api_request(endpoint, params, headers):
        # Implement the logic to make the actual API request
        # based on the endpoint, params, and headers
        # Return the response data
        return {'data': 'Sample response data'}

    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5001, debug=debug_mode)
