import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration du microservice DeID"""
    
    # Base de données source (données originales)
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
    
    # Flask
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Faker
    FAKER_SEED = int(os.getenv('FAKER_SEED', 42))
    
    # Règles d'anonymisation
    ANONYMIZATION_RULES = {
        'keep_gender': True,
        'keep_birth_year': True,
        'shift_dates': True,
        'date_shift_days': 30,
        'keep_zip_code_prefix': True,
        'redact_ssn': True,
    }

class DevelopmentConfig(Config):
    """Configuration développement"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuration production"""
    DEBUG = False
    FAKER_SEED = None

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
