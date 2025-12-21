import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration du microservice ML Predictor"""
    
    # Base de données
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5433')
    DB_NAME = os.getenv('DB_NAME', 'healthflow_fhir')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'qwerty')
    
    # URI SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # Pool de connexions PostgreSQL (AJOUTÉ)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 40,
        'pool_timeout': 120,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Flask
    PORT = int(os.getenv('PORT', 5002))
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Seuils de risque
    RISK_THRESHOLDS = {
        'low': 7.5,      # < 7.5%
        'moderate': 20,  # 7.5% - 20%
        'high': 100      # > 20%
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
