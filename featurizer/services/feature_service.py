from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from config import Config
from models.feature_vector import PatientFeatures
from extractors.patient_features import PatientFeatureExtractor
from extractors.vital_signs_features import VitalSignsFeatureExtractor
from extractors.lab_results_features import LabResultsFeatureExtractor
from services.clinical_nlp import ClinicalNLPExtractor
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class FeatureExtractionService:
    def __init__(self):
        self.engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        self.Session = sessionmaker(bind=self.engine)
        self.patient_extractor = PatientFeatureExtractor()
        self.vitals_extractor = VitalSignsFeatureExtractor()
        self.labs_extractor = LabResultsFeatureExtractor()
        self.nlp_extractor = ClinicalNLPExtractor()

    def extract_features(self, patient_id):
        session = self.Session()
        try:
            # Check existing records
            existing = session.query(PatientFeatures).filter_by(patient_id=patient_id).first()
            
            # Fetch FHIR data
            query = text("""
                SELECT resource_data 
                FROM fhir_resources_anonymized 
                WHERE anonymized_fhir_id = :patient_id 
                AND resource_type = 'Patient'
            """)
            patient_result = session.execute(query, {'patient_id': patient_id}).fetchone()
            
            all_features = {}
            
            if patient_result:
                # Full extraction from FHIR
                patient_data = json.loads(patient_result[0]) if isinstance(patient_result[0], str) else patient_result[0]
                
                obs_query = text("""
                    SELECT resource_data 
                    FROM fhir_resources_anonymized 
                    WHERE resource_data::json->'subject'->>'reference' = :patient_ref
                    AND resource_type = 'Observation'
                """)
                obs_results = session.execute(obs_query, {'patient_ref': f'Patient/{patient_id}'}).fetchall()
                observations = [json.loads(row[0]) if isinstance(row[0], str) else row[0] for row in obs_results]
                
                patient_features = self.patient_extractor.extract(patient_data)
                vitals_features = self.vitals_extractor.extract(observations)
                labs_features = self.labs_extractor.extract(observations)
                
                # Clinical features calculation
                clinical_features = {}
                if observations:
                    clinical_features['total_observations'] = len(observations)
                    dates = []
                    for obs in observations:
                        if 'effectiveDateTime' in obs:
                            try:
                                date = datetime.fromisoformat(obs['effectiveDateTime'].replace('Z', '+00:00'))
                                dates.append(date)
                            except:
                                pass
                    if len(dates) > 1:
                        dates.sort()
                        span = (dates[-1] - dates[0]).days
                        clinical_features['observation_span_days'] = span
                        clinical_features['consultation_frequency'] = round(len(observations) / max(span, 1), 4)
                
                all_features.update({**patient_features, **vitals_features, **labs_features, **clinical_features})
                
            elif existing:
                # Fallback to existing data
                all_features = existing.features_json or {}
            else:
                return None, "Patient not found and no existing record"

            # Fetch clinical notes
            notes_query = text("SELECT note_text FROM clinical_notes WHERE patient_id = :patient_id")
            try:
                notes_results = session.execute(notes_query, {'patient_id': patient_id}).fetchall()
                clinical_notes = [row[0] for row in notes_results if row[0]]
            except Exception as e:
                logger.warning(f"Could not fetch notes: {e}")
                clinical_notes = []
            
            # NLP Extraction
            nlp_features = self.nlp_extractor.extract_clinical_features(clinical_notes)
            all_features.update(nlp_features)
            
            # Save/Update
            if existing:
                for key, value in all_features.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.features_json = all_features
                existing.extraction_date = datetime.utcnow()
            else:
                feature_record = PatientFeatures(
                    patient_id=patient_id,
                    age=all_features.get('age'),
                    gender=all_features.get('gender'),
                    bmi=all_features.get('bmi'),
                    avg_systolic_bp=all_features.get('avg_systolic_bp'),
                    avg_diastolic_bp=all_features.get('avg_diastolic_bp'),
                    height_cm=all_features.get('height_cm'),
                    weight_kg=all_features.get('weight_kg'),
                    avg_cholesterol=all_features.get('avg_cholesterol'),
                    avg_hdl=all_features.get('avg_hdl'),
                    avg_ldl=all_features.get('avg_ldl'),
                    avg_triglycerides=all_features.get('avg_triglycerides'),
                    avg_hemoglobin=all_features.get('avg_hemoglobin'),
                    total_observations=all_features.get('total_observations'),
                    observation_span_days=all_features.get('observation_span_days'),
                    consultation_frequency=all_features.get('consultation_frequency'),
                    
                    # NLP Features
                    nlp_num_conditions=all_features.get('nlp_num_conditions'),
                    nlp_has_diabetes=all_features.get('nlp_has_diabetes'),
                    nlp_has_hypertension=all_features.get('nlp_has_hypertension'),
                    nlp_has_chf=all_features.get('nlp_has_chf'),
                    nlp_has_copd=all_features.get('nlp_has_copd'),
                    nlp_has_ckd=all_features.get('nlp_has_ckd'),
                    nlp_num_medications=all_features.get('nlp_num_medications'),
                    nlp_polypharmacy=all_features.get('nlp_polypharmacy'),
                    nlp_num_symptoms=all_features.get('nlp_num_symptoms'),
                    nlp_has_pain=all_features.get('nlp_has_pain'),
                    nlp_has_dyspnea=all_features.get('nlp_has_dyspnea'),
                    nlp_note_length=all_features.get('nlp_note_length'),
                    nlp_note_count=all_features.get('nlp_note_count'),
                    nlp_avg_note_length=all_features.get('nlp_avg_note_length'),
                    
                    features_json=all_features
                )
                session.add(feature_record)
            
            session.commit()
            return all_features, "success"
            
        except Exception as e:
            session.rollback()
            logger.error(f"Extraction error: {e}")
            return None, str(e)
        finally:
            session.close()
