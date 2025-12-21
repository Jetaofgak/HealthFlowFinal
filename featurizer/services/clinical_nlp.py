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
            'num_comorbidities': len(conditions),
            'has_diabetes': int('diabetes' in str(conditions).lower()),
            'has_hypertension': int('hypertension' in str(conditions).lower()),
            'has_chf': int('chf' in str(conditions).lower() or 'heart failure' in str(conditions).lower()),

            # Medication count
            'num_medications': len(medications),
            'polypharmacy': int(len(medications) >= 5),

            # Text complexity metrics
            'note_length': len(combined_text),
            'note_count': len(clinical_notes),
            'avg_note_length': len(combined_text) / len(clinical_notes) if clinical_notes else 0,

            # Extracted entities (for reference)
            'conditions_mentioned': conditions,
            'medications_mentioned': medications
        }

        return features

    def _empty_features(self) -> Dict[str, any]:
        """Return empty feature dict"""
        return {
            'num_comorbidities': 0,
            'has_diabetes': 0,
            'has_hypertension': 0,
            'has_chf': 0,
            'num_medications': 0,
            'polypharmacy': 0,
            'note_length': 0,
            'note_count': 0,
            'avg_note_length': 0,
            'conditions_mentioned': [],
            'medications_mentioned': []
        }