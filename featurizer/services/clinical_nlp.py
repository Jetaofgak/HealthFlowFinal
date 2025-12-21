from typing import Dict, List
import logging
from .biobert_service import BioBERTService

logger = logging.getLogger(__name__)

class ClinicalNLPExtractor:
    """Extract features from clinical notes using NLP"""

    def __init__(self):
        self.biobert = BioBERTService()

    def extract_clinical_features(self, clinical_notes: List[str]) -> Dict[str, any]:
        """
        Extract structured features from clinical notes

        Args:
            clinical_notes: List of clinical note texts

        Returns:
            Dictionary of extracted features
        """
        # Combine all notes
        combined_text = " ".join(clinical_notes) if clinical_notes else ""

        if not combined_text:
            return self._empty_features()

        # Extract medical entities
        entities = self.biobert.extract_medical_entities(combined_text)

        # Count comorbidities
        conditions = entities.get('conditions', [])
        medications = entities.get('medications', [])

        features = {
            # Comorbidity counts
            'nlp_num_conditions': len(conditions),
            'nlp_has_diabetes': int('diabetes' in str(conditions).lower()),
            'nlp_has_hypertension': int('hypertension' in str(conditions).lower()),
            'nlp_has_chf': int('chf' in str(conditions).lower() or 'heart failure' in str(conditions).lower()),
            'nlp_has_copd': int('copd' in str(conditions).lower() or 'chronic obstructive' in str(conditions).lower()),
            'nlp_has_ckd': int('ckd' in str(conditions).lower() or 'chronic kidney' in str(conditions).lower()),

            # Medication count
            'nlp_num_medications': len(medications),
            'nlp_polypharmacy': int(len(medications) >= 5),

            # Text complexity metrics
            'nlp_note_length': len(combined_text),
            'nlp_note_count': len(clinical_notes),
            'nlp_avg_note_length': len(combined_text) / len(clinical_notes) if clinical_notes else 0,

            # Extracted entities (for reference)
            'nlp_conditions_mentioned': conditions,
            'nlp_medications_mentioned': medications,
            
            # Symptom indicators (adding to match model)
            'nlp_num_symptoms': 0, # Placeholder as logic was missing in valid extraction block
            'nlp_has_pain': 0,
            'nlp_has_dyspnea': 0
        }

        return features

    def _empty_features(self) -> Dict[str, any]:
        """Return empty feature dict"""
        return {
            'nlp_num_conditions': 0,
            'nlp_has_diabetes': 0,
            'nlp_has_hypertension': 0,
            'nlp_has_chf': 0,
            'nlp_has_copd': 0,
            'nlp_has_ckd': 0,
            'nlp_num_medications': 0,
            'nlp_polypharmacy': 0,
            'nlp_note_length': 0,
            'nlp_note_count': 0,
            'nlp_avg_note_length': 0,
            'nlp_conditions_mentioned': [],
            'nlp_medications_mentioned': [],
            'nlp_num_symptoms': 0,
            'nlp_has_pain': 0,
            'nlp_has_dyspnea': 0
        }