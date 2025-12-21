from flask import Blueprint, request, jsonify
from middleware.auth import require_jwt
import requests
import logging
import os

score_bp = Blueprint('scores', __name__)
logger = logging.getLogger(__name__)

ML_PREDICTOR_URL = os.getenv('ML_PREDICTOR_URL', 'http://localhost:5002')

@score_bp.route('/scores/patient/<patient_id>', methods=['GET'])
@require_jwt
def get_patient_score(patient_id):
    """
    Get readmission risk score for a specific patient
    Requires valid JWT token
    """
    try:
        # In a real implementation, fetch features from database
        # For now, proxy to ML Predictor service

        # Mock features (in production, fetch from database)
        mock_features = {
            'age': 65,
            'num_medications': 8,
            'prior_admissions': 2,
            'has_diabetes': 1,
            'has_hypertension': 1
        }

        # Call ML Predictor
        response = requests.post(
            f"{ML_PREDICTOR_URL}/api/v1/predictions/readmission",
            json={
                'patient_id': patient_id,
                'features': mock_features
            },
            timeout=10
        )

        if response.status_code != 200:
            return jsonify({'error': 'Prediction service error'}), 503

        return jsonify(response.json()), 200

    except requests.RequestException as e:
        logger.error(f"ML Predictor request failed: {str(e)}")
        return jsonify({'error': 'Prediction service unavailable'}), 503
    except Exception as e:
        logger.error(f"Score retrieval error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@score_bp.route('/scores/batch', methods=['POST'])
@require_jwt
def get_batch_scores():
    """
    Get risk scores for multiple patients

    Request body:
    {
        "patient_ids": ["patient1", "patient2", ...]
    }
    """
    try:
        data = request.get_json()
        patient_ids = data.get('patient_ids', [])

        if not patient_ids:
            return jsonify({'error': 'No patient IDs provided'}), 400

        results = []
        for patient_id in patient_ids:
            # In production, fetch features from database
            mock_features = {
                'age': 65,
                'num_medications': 8,
                'prior_admissions': 2
            }

            response = requests.post(
                f"{ML_PREDICTOR_URL}/api/v1/predictions/readmission",
                json={'patient_id': patient_id, 'features': mock_features},
                timeout=10
            )

            if response.status_code == 200:
                results.append(response.json())

        return jsonify({'predictions': results}), 200

    except Exception as e:
        logger.error(f"Batch score error: {str(e)}")
        return jsonify({'error': str(e)}), 500
