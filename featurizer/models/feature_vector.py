from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PatientFeatures(Base):
    """Modèle pour stocker les features extraites des patients"""
    __tablename__ = 'patient_features'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String(255), unique=True, nullable=False)
    
    # Features démographiques
    age = Column(Integer)
    gender = Column(String(10))
    
    # Features vitales
    bmi = Column(Float)
    avg_systolic_bp = Column(Float)
    avg_diastolic_bp = Column(Float)
    avg_heart_rate = Column(Float)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    
    # Features laboratoires
    avg_cholesterol = Column(Float)
    avg_hdl = Column(Float)
    avg_ldl = Column(Float)
    avg_triglycerides = Column(Float)
    avg_hemoglobin = Column(Float)
    
    # Features cliniques
    total_observations = Column(Integer)
    observation_span_days = Column(Integer)
    consultation_frequency = Column(Float)
    
    # NLP Features
    nlp_num_conditions = Column(Integer)
    nlp_has_diabetes = Column(Integer)
    nlp_has_hypertension = Column(Integer)
    nlp_has_chf = Column(Integer)
    nlp_has_copd = Column(Integer)
    nlp_has_ckd = Column(Integer)
    
    nlp_num_medications = Column(Integer)
    nlp_polypharmacy = Column(Integer)
    
    nlp_num_symptoms = Column(Integer)
    nlp_has_pain = Column(Integer)
    nlp_has_dyspnea = Column(Integer)
    
    nlp_note_length = Column(Integer)
    nlp_note_count = Column(Integer)
    nlp_avg_note_length = Column(Float)
    
    # Métadonnées
    features_json = Column(JSON)  # Toutes les features en JSON
    extraction_date = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PatientFeatures(patient_id={self.patient_id}, age={self.age}, bmi={self.bmi})>"
    
    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'patient_id': self.patient_id,
            'demographics': {
                'age': self.age,
                'gender': self.gender
            },
            'vitals': {
                'bmi': self.bmi,
                'avg_systolic_bp': self.avg_systolic_bp,
                'avg_diastolic_bp': self.avg_diastolic_bp,
                'avg_heart_rate': self.avg_heart_rate,
                'height_cm': self.height_cm,
                'weight_kg': self.weight_kg
            },
            'labs': {
                'avg_cholesterol': self.avg_cholesterol,
                'avg_hdl': self.avg_hdl,
                'avg_ldl': self.avg_ldl,
                'avg_triglycerides': self.avg_triglycerides,
                'avg_hemoglobin': self.avg_hemoglobin
            },
            'clinical_history': {
                'total_observations': self.total_observations,
                'observation_span_days': self.observation_span_days,
                'consultation_frequency': self.consultation_frequency
            },
            # NLP Features (flat structure for consistency)
            'nlp_num_conditions': self.nlp_num_conditions,
            'nlp_has_diabetes': self.nlp_has_diabetes,
            'nlp_has_hypertension': self.nlp_has_hypertension,
            'nlp_has_chf': self.nlp_has_chf,
            'nlp_has_copd': self.nlp_has_copd,
            'nlp_has_ckd': self.nlp_has_ckd,
            'nlp_num_medications': self.nlp_num_medications,
            'nlp_polypharmacy': self.nlp_polypharmacy,
            'nlp_num_symptoms': self.nlp_num_symptoms,
            'nlp_has_pain': self.nlp_has_pain,
            'nlp_has_dyspnea': self.nlp_has_dyspnea,
            'nlp_note_length': self.nlp_note_length,
            'nlp_note_count': self.nlp_note_count,
            'nlp_avg_note_length': self.nlp_avg_note_length,
            
            'extraction_date': self.extraction_date.isoformat() if self.extraction_date else None
        }
 
