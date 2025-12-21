import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration du microservice Featurizer"""
    
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
    PORT = int(os.getenv('PORT', 5001))
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Configuration des features
    FEATURE_CONFIG = {
        'age_bins': [0, 18, 30, 40, 50, 60, 70, 100],
        'bmi_categories': {
            'underweight': (0, 18.5),
            'normal': (18.5, 25),
            'overweight': (25, 30),
            'obese': (30, 100)
        },
        'bp_categories': {
            'normal': (0, 120),
            'elevated': (120, 130),
            'hypertension_stage1': (130, 140),
            'hypertension_stage2': (140, 200)
        }
    }

class DevelopmentConfig(Config):
    """Configuration développement"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuration production"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
