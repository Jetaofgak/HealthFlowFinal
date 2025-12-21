from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from config import config
from routes.score_routes import score_bp
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Factory to create Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # JWT
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(score_bp, url_prefix='/api/v1')

    # Health check
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'score-api'
        }), 200

    # Demo login endpoint (for testing only)
    @app.route('/api/v1/auth/login', methods=['POST'])
    def login():
        """Demo login endpoint - returns JWT token"""
        # In production, validate credentials against database
        access_token = create_access_token(identity={'user_id': 'demo', 'role': 'clinician'})
        return jsonify({'access_token': access_token}), 200

    logger.info("ScoreAPI microservice started successfully")

    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
