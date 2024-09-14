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

    @app.route('/api/config')
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

    # ... rest of your routes ...

    return app

if __name__ == '__main__':
    app = create_app()
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5001, debug=debug_mode)
