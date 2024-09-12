from flask import Flask, render_template, jsonify
from flask_migrate import Migrate
from extensions import db
from api import fleet, maintenance, rebalancing, user, reporting, integration, future_modules
import os
import logging

def create_app():
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(filename='app.log', level=logging.ERROR)
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

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"404 error: {error}")
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"500 error: {error}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({"error": "An unexpected error occurred. Please try again later or contact support."}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
