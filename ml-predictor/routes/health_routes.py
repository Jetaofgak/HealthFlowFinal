from flask import Blueprint, jsonify
import logging
import os

health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)

def _model_exists() -> bool:
    requested = os.getenv('XGBOOST_MODEL_PATH', '../xgboost_readmission_model.ubj')
    candidates = [requested]

    if requested.endswith('.ubj'):
        candidates.append(requested[:-4] + '.json')
    elif requested.endswith('.json'):
        candidates.insert(0, requested[:-5] + '.ubj')

    return any(os.path.exists(path) for path in candidates)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        model_exists = _model_exists()

        return jsonify({
            'status': 'healthy' if model_exists else 'degraded',
            'service': 'ml-predictor',
            'model_loaded': model_exists
        }), 200 if model_exists else 503
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'ml-predictor',
            'error': str(e)
        }), 503
