from flask import Blueprint, jsonify
from database.connection import DatabaseManager
import logging

health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from config import config
        from sqlalchemy import text
        db_manager = DatabaseManager(config['development'].SQLALCHEMY_DATABASE_URI)
        
        with db_manager.get_session() as session:
            session.execute(text('SELECT 1'))

        return jsonify({
            'status': 'healthy',
            'service': 'deID',
            'database': 'connected'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'deID',
            'error': str(e)
        }), 503