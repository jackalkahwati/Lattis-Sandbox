from flask import Flask, render_template, jsonify
from extensions import db
from api import fleet, maintenance, rebalancing, user, reporting, integration
import os

def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(fleet.bp)
    app.register_blueprint(maintenance.bp)
    app.register_blueprint(rebalancing.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(reporting.bp)
    app.register_blueprint(integration.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
