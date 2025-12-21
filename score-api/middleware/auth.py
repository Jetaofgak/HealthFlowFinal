from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import logging

logger = logging.getLogger(__name__)

def require_jwt(fn):
    """Decorator to require valid JWT token"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return jsonify({'error': 'Invalid or missing authentication token'}), 401
    return wrapper

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt_identity()

            if not isinstance(claims, dict) or claims.get('role') != 'admin':
                return jsonify({'error': 'Admin access required'}), 403

            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Admin check failed: {str(e)}")
            return jsonify({'error': 'Unauthorized'}), 401
    return wrapper
