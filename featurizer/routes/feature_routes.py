from flask import Blueprint, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.feature_vector import PatientFeatures, Base
from extractors.patient_features import PatientFeatureExtractor
from extractors.vital_signs_features import VitalSignsFeatureExtractor
from extractors.lab_results_features import LabResultsFeatureExtractor
from services.clinical_nlp import ClinicalNLPExtractor
from config import Config
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

feature_bp = Blueprint('features', __name__)

# Initialisation DB
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Initialisation des extracteurs
patient_extractor = PatientFeatureExtractor()
vitals_extractor = VitalSignsFeatureExtractor()
labs_extractor = LabResultsFeatureExtractor()
nlp_extractor = ClinicalNLPExtractor()

@feature_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'UP',
        'service': 'Featurizer'
    })

from services.feature_service import FeatureExtractionService

extraction_service = FeatureExtractionService()

@feature_bp.route('/extract/patient/<patient_id>', methods=['POST'])
def extract_patient_features(patient_id):
    """Extrait les features d'un patient spécifique"""
    features, status = extraction_service.extract_features(patient_id)
    
    if features:
        return jsonify({
            'status': 'success',
            'patient_id': patient_id,
            'features': features
        }), 200
    elif status == "Patient not found and no existing record":
        return jsonify({'error': status}), 404
    else:
        return jsonify({'error': status}), 500

@feature_bp.route('/extract/all', methods=['POST'])
def extract_all_features():
    """Extrait les features de tous les patients existants"""
    try:
        session = Session()
        # Retrieve all patient IDs from the reliable source (patient_features)
        from sqlalchemy import text
        query = text("SELECT patient_id FROM patient_features")
        patients = session.execute(query).fetchall()
        session.close()
        
        results = []
        errors = []
        
        for patient in patients:
            patient_id = patient[0]
            try:
                features, status = extraction_service.extract_features(patient_id)
                if features:
                    results.append(patient_id)
                else:
                    errors.append({'patient_id': patient_id, 'error': status})
            except Exception as e:
                errors.append({'patient_id': patient_id, 'error': str(e)})
        
        return jsonify({
            'status': 'success',
            'extracted': len(results),
            'errors': len(errors),
            'patient_ids': results,
            'error_details': errors
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk extraction: {e}")
        return jsonify({'error': str(e)}), 500

@feature_bp.route('/features/<patient_id>', methods=['GET'])
def get_patient_features(patient_id):
    """Récupère les features d'un patient"""
    try:
        session = Session()
        features = session.query(PatientFeatures).filter_by(patient_id=patient_id).first()
        session.close()
        
        if not features:
            return jsonify({'error': 'Features not found'}), 404
        
        return jsonify(features.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error retrieving features: {e}")
        return jsonify({'error': str(e)}), 500

@feature_bp.route('/stats', methods=['GET'])
def get_stats():
    """Statistiques sur les features extraites"""
    try:
        session = Session()
        
        from sqlalchemy import func
        
        total = session.query(func.count(PatientFeatures.id)).scalar()
        
        avg_age = session.query(func.avg(PatientFeatures.age)).scalar()
        avg_bmi = session.query(func.avg(PatientFeatures.bmi)).scalar()
        avg_cholesterol = session.query(func.avg(PatientFeatures.avg_cholesterol)).scalar()
        
        session.close()
        
        return jsonify({
            'total_patients': total,
            'average_age': round(avg_age, 1) if avg_age else None,
            'average_bmi': round(avg_bmi, 2) if avg_bmi else None,
            'average_cholesterol': round(avg_cholesterol, 2) if avg_cholesterol else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@feature_bp.route('/features', methods=['GET'])
def list_all_features():
    """Liste toutes les features extraites"""
    try:
        session = Session()
        all_features = session.query(PatientFeatures).all()
        session.close()
        
        return jsonify({
            'total': len(all_features),
            'features': [f.to_dict() for f in all_features]
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing features: {e}")
        return jsonify({'error': str(e)}), 500
 
