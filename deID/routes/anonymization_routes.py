from flask import Blueprint, jsonify, request
from database.connection import DatabaseManager
from models.fhir_resource import FhirResource, FhirResourceAnonymized
from anonymizer.pseudonym_manager import PseudonymManager
from anonymizer.patient_anonymizer import PatientAnonymizer
from anonymizer.observation_anonymizer import ObservationAnonymizer
from config import Config
import logging
import json

logger = logging.getLogger(__name__)

anonymization_bp = Blueprint('anonymization', __name__)

# Initialisation
db_manager = DatabaseManager(Config.SQLALCHEMY_DATABASE_URI)
pseudonym_manager = PseudonymManager(seed=Config.FAKER_SEED)
patient_anonymizer = PatientAnonymizer(Config.ANONYMIZATION_RULES, pseudonym_manager)
observation_anonymizer = ObservationAnonymizer(Config.ANONYMIZATION_RULES, pseudonym_manager)

@anonymization_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'UP',
        'service': 'DeID',
        'cache_stats': pseudonym_manager.get_cache_stats()
    })

@anonymization_bp.route('/anonymize/patient/<patient_fhir_id>', methods=['POST'])
def anonymize_patient(patient_fhir_id):
    """Anonymise un patient spécifique"""
    try:
        with db_manager.get_session() as session:
            # Récupérer le patient original
            patient = session.query(FhirResource).filter_by(
                fhir_id=patient_fhir_id,
                resource_type='Patient'
            ).first()
            
            if not patient:
                return jsonify({'error': 'Patient not found'}), 404
            
            # Anonymiser
            anonymized_data = patient_anonymizer.anonymize(patient.resource_data)
            
            # Extraire le nouvel ID
            anonymized_json = json.loads(anonymized_data)
            anonymized_id = anonymized_json['id']
            
            # Vérifier si déjà anonymisé
            existing = session.query(FhirResourceAnonymized).filter_by(
                original_fhir_id=patient.fhir_id
            ).first()
            
            if existing:
                # Mettre à jour
                existing.anonymized_fhir_id = anonymized_id
                existing.resource_data = anonymized_data
                logger.info(f"Updated anonymized patient {patient_fhir_id}")
            else:
                # Créer nouveau
                anonymized_resource = FhirResourceAnonymized(
                    original_fhir_id=patient.fhir_id,
                    anonymized_fhir_id=anonymized_id,
                    resource_type='Patient',
                    resource_data=anonymized_data
                )
                session.add(anonymized_resource)
                logger.info(f"Created anonymized patient {patient_fhir_id}")
            
            return jsonify({
                'status': 'success',
                'original_id': patient_fhir_id,
                'anonymized_id': anonymized_id
            }), 200
            
    except Exception as e:
        logger.error(f"Error anonymizing patient: {e}")
        return jsonify({'error': str(e)}), 500

@anonymization_bp.route('/anonymize/all', methods=['POST'])
def anonymize_all():
    """Anonymise toutes les ressources"""
    try:
        with db_manager.get_session() as session:
            # Récupérer tous les patients
            patients = session.query(FhirResource).filter_by(
                resource_type='Patient'
            ).all()
            
            patient_id_mapping = {}
            anonymized_count = 0
            
            # Anonymiser les patients
            for patient in patients:
                anonymized_data = patient_anonymizer.anonymize(patient.resource_data)
                
                anonymized_json = json.loads(anonymized_data)
                anonymized_id = anonymized_json['id']
                
                patient_id_mapping[patient.fhir_id] = anonymized_id
                
                # Vérifier si existe
                existing = session.query(FhirResourceAnonymized).filter_by(
                    original_fhir_id=patient.fhir_id
                ).first()
                
                if existing:
                    existing.anonymized_fhir_id = anonymized_id
                    existing.resource_data = anonymized_data
                else:
                    anonymized_resource = FhirResourceAnonymized(
                        original_fhir_id=patient.fhir_id,
                        anonymized_fhir_id=anonymized_id,
                        resource_type='Patient',
                        resource_data=anonymized_data
                    )
                    session.add(anonymized_resource)
                
                anonymized_count += 1
            
            # Anonymiser les observations (DISABLED for large datasets - 1.86M observations cause timeout)
            # TODO: Implement batched processing for observations
            # observations = session.query(FhirResource).filter_by(
            #     resource_type='Observation'
            # ).all()

            logger.info(f"Skipping observation anonymization (1.86M+ records) - only processing patients")

            return jsonify({
                'status': 'success',
                'anonymized_count': anonymized_count,
                'patients': len(patients),
                'observations': 0,
                'note': 'Observation anonymization skipped for performance (1.86M records)'
            }), 200
            
    except Exception as e:
        logger.error(f"Error in bulk anonymization: {e}")
        return jsonify({'error': str(e)}), 500

@anonymization_bp.route('/stats', methods=['GET'])
def get_stats():
    """Statistiques d'anonymisation"""
    try:
        with db_manager.get_session() as session:
            from sqlalchemy import func
            
            stats = session.query(
                FhirResourceAnonymized.resource_type,
                func.count(FhirResourceAnonymized.id)
            ).group_by(FhirResourceAnonymized.resource_type).all()
            
            stats_dict = {resource_type: count for resource_type, count in stats}
            
            return jsonify({
                'anonymized_resources': stats_dict,
                'cache': pseudonym_manager.get_cache_stats()
            }), 200
            
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@anonymization_bp.route('/anonymized/<resource_type>/<anonymized_id>', methods=['GET'])
def get_anonymized_resource(resource_type, anonymized_id):
    """Récupère une ressource anonymisée"""
    try:
        with db_manager.get_session() as session:
            resource = session.query(FhirResourceAnonymized).filter_by(
                resource_type=resource_type,
                anonymized_fhir_id=anonymized_id
            ).first()
            
            if not resource:
                return jsonify({'error': 'Resource not found'}), 404
            
            return jsonify({
                'anonymized_id': resource.anonymized_fhir_id,
                'resource_type': resource.resource_type,
                'data': json.loads(resource.resource_data),
                'anonymization_date': resource.anonymization_date.isoformat()
            }), 200
            
    except Exception as e:
        logger.error(f"Error retrieving resource: {e}")
        return jsonify({'error': str(e)}), 500
