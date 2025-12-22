from flask import Flask
from flask_cors import CORS
from config import config
from routes.anonymization_routes import anonymization_bp
from database.connection import DatabaseManager, Base
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # CORS - Allow all origins for all routes (including /health)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Enregistrer les blueprints
    from routes.health_routes import health_bp

    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(anonymization_bp, url_prefix='/api/v1')
    
    # Créer les tables si nécessaire
    db_manager = DatabaseManager(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(db_manager.engine)
    
    logger.info("DeID microservice started successfully")
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(
        host='0.0.0.0',
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
