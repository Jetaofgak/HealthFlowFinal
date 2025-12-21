from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class BioBERTService:
    """Service for biomedical named entity recognition using BioBERT"""

    def __init__(self, model_name: str = "dmis-lab/biobert-base-cased-v1.1"):
        self.model_name = model_name
        self.ner_pipeline = None
        self.load_model()

    def load_model(self):
        """Load BioBERT model for NER"""
        try:
            logger.info(f"Loading BioBERT model: {self.model_name}")

            # Note: Using a BioBERT-based NER model
            # For actual medical NER, consider using a fine-tuned model like:
            # "d4data/biomedical-ner-all" or "allenai/scibert_scivocab_uncased"

            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForTokenClassification.from_pretrained("d4data/biomedical-ner-all")

            self.ner_pipeline = pipeline(
                "ner",
                model=model,
                tokenizer=tokenizer,
                aggregation_strategy="simple"
            )

            logger.info("BioBERT NER model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load BioBERT model: {str(e)}")
            # Fallback to simple extraction if model fails
            self.ner_pipeline = None

    def extract_medical_entities(self, clinical_text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from clinical notes

        Args:
            clinical_text: Raw clinical note text

        Returns:
            Dictionary with entity types and extracted entities
        """
        if not clinical_text:
            return {}

        try:
            if self.ner_pipeline is None:
                # Fallback: simple keyword extraction
                return self._simple_entity_extraction(clinical_text)

            # Run BioBERT NER
            entities = self.ner_pipeline(clinical_text)

            # Group entities by type
            entity_dict = {}
            for entity in entities:
                entity_type = entity['entity_group']
                entity_text = entity['word']

                if entity_type not in entity_dict:
                    entity_dict[entity_type] = []

                if entity_text not in entity_dict[entity_type]:
                    entity_dict[entity_type].append(entity_text)

            return entity_dict

        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return self._simple_entity_extraction(clinical_text)

    def _simple_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """Fallback simple keyword-based extraction"""
        import re

        # Common medical keywords
        conditions = ['diabetes', 'hypertension', 'copd', 'chf', 'mi', 'stroke',
                     'pneumonia', 'sepsis', 'uti', 'cancer']
        medications = ['aspirin', 'metformin', 'insulin', 'lisinopril', 'atorvastatin',
                      'warfarin', 'heparin', 'furosemide']

        text_lower = text.lower()

        found_entities = {
            'conditions': [c for c in conditions if c in text_lower],
            'medications': [m for m in medications if m in text_lower]
        }

        return {k: v for k, v in found_entities.items() if v}