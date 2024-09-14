from flask import Flask, render_template, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from extensions import db
from api import fleet, maintenance, rebalancing, user, reporting, integration, future_modules, auth, vehicle, trip, payment, geofencing, pricing
import os
import logging
from dotenv import load_dotenv

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
                    {'method': 'GET', 'path': '/api/v1/auth/roles'},
                    {'method': 'POST', 'path': '/api/v1/auth/roles'},
                    {'method': 'PUT', 'path': '/api/v1/auth/roles/{roleId}'},
                    {'method': 'DELETE', 'path': '/api/v1/auth/roles/{roleId}'},
                    {'method': 'POST', 'path': '/api/v1/users/{userId}/roles/{roleId}'},
                    {'method': 'DELETE', 'path': '/api/v1/users/{userId}/roles/{roleId}'},
                ],
                'Vehicle Management': [
                    {'method': 'POST', 'path': '/api/v1/vehicles'},
                    {'method': 'PATCH', 'path': '/api/v1/vehicles/{vehicleId}'},
                    {'method': 'DELETE', 'path': '/api/v1/vehicles/{vehicleId}'},
                    {'method': 'GET', 'path': '/api/v1/vehicles/{vehicleId}'},
                    {'method': 'GET', 'path': '/api/v1/vehicles'},
                ],
                'Fleet Management': [
                    {'method': 'POST', 'path': '/api/v1/fleets'},
                    {'method': 'PATCH', 'path': '/api/v1/fleets/{fleetId}'},
                    {'method': 'DELETE', 'path': '/api/v1/fleets/{fleetId}'},
                    {'method': 'GET', 'path': '/api/v1/fleets/{fleetId}'},
                    {'method': 'GET', 'path': '/api/v1/fleets'},
                ],
                'Trip Management': [
                    {'method': 'POST', 'path': '/api/v1/trips'},
                    {'method': 'PATCH', 'path': '/api/v1/trips/{tripId}'},
                    {'method': 'GET', 'path': '/api/v1/trips/{tripId}'},
                    {'method': 'GET', 'path': '/api/v1/trips'},
                ],
                'Maintenance & Alerts': [
                    {'method': 'POST', 'path': '/api/v1/maintenance'},
                    {'method': 'PATCH', 'path': '/api/v1/maintenance/{maintenanceId}'},
                    {'method': 'GET', 'path': '/api/v1/vehicles/{vehicleId}/maintenance'},
                    {'method': 'GET', 'path': '/api/v1/maintenance'},
                    {'method': 'POST', 'path': '/api/v1/alerts'},
                    {'method': 'GET', 'path': '/api/v1/alerts'},
                ],
                'Analytics & Reporting': [
                    {'method': 'GET', 'path': '/api/v1/analytics/usage'},
                    {'method': 'POST', 'path': '/api/v1/reports'},
                    {'method': 'GET', 'path': '/api/v1/reports/{reportId}'},
                    {'method': 'GET', 'path': '/api/v1/reports'},
                ],
                'Payment & Billing': [
                    {'method': 'POST', 'path': '/api/v1/invoices'},
                    {'method': 'GET', 'path': '/api/v1/invoices/{invoiceId}'},
                    {'method': 'GET', 'path': '/api/v1/invoices'},
                    {'method': 'POST', 'path': '/api/v1/payments'},
                    {'method': 'GET', 'path': '/api/v1/billing/history'},
                ],
                'Location & Geofencing': [
                    {'method': 'POST', 'path': '/api/v1/geofences'},
                    {'method': 'PATCH', 'path': '/api/v1/geofences/{geofenceId}'},
                    {'method': 'DELETE', 'path': '/api/v1/geofences/{geofenceId}'},
                    {'method': 'GET', 'path': '/api/v1/geofences/{geofenceId}'},
                    {'method': 'GET', 'path': '/api/v1/geofences'},
                ],
                'Additional Fleet Management': [
                    {'method': 'GET', 'path': '/api/vehicles'},
                    {'method': 'POST', 'path': '/api/tasks'},
                    {'method': 'PUT', 'path': '/api/vehicles/{id}'},
                    {'method': 'GET', 'path': '/api/stats'},
                ],
                'Dynamic Pricing': [
                    {'method': 'POST', 'path': '/api/v1/pricing/base'},
                    {'method': 'POST', 'path': '/api/v1/pricing/surge'},
                ],
            }
        }
        return jsonify(api_config)

    # ... (keep all other existing route handlers)

    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5001, debug=debug_mode)
