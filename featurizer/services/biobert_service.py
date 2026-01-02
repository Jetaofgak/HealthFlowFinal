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
        """Load OpenMed NER model for better biomedical entity detection"""
        try:
            import torch
            logger.info(f"Loading OpenMed NER model (optimized for diseases/conditions)")

            # Use OpenMed's state-of-the-art disease detection model
            # Achieves 92.7% F1 on BC5CDR-Disease (vs 85% for d4data/biomedical-ner-all)
            model_name_ner = "OpenMed/OpenMed-NER-DiseaseDetect-SuperMedical-125M"
            
            tokenizer = AutoTokenizer.from_pretrained(model_name_ner)
            model = AutoModelForTokenClassification.from_pretrained(model_name_ner)

            # Enable MPS acceleration on Apple Silicon (2-5x speedup)
            # Falls back to CPU if MPS not available
            # Enable CUDA (NVIDIA) or MPS (Apple) acceleration
            if torch.cuda.is_available():
                device = 0
                logger.info("Using device: CUDA (NVIDIA GPU)")
            elif torch.backends.mps.is_available():
                device = 0
                logger.info("Using device: MPS (Apple Silicon)")
            else:
                device = -1
                logger.info("Using device: CPU")

            self.ner_pipeline = pipeline(
                "ner",
                model=model,
                tokenizer=tokenizer,
                aggregation_strategy="max",  # Better for handling split words
                device=device
            )

            logger.info("OpenMed NER model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load OpenMed model: {str(e)}")
            logger.info("Falling back to keyword-based extraction")
            # Fallback to simple extraction if model fails
            self.ner_pipeline = None

    def extract_medical_entities(self, clinical_text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from clinical notes using hybrid approach:
        - OpenMed NER for complex disease detection
        - Keyword extraction for medications and simple conditions
        
        Args:
            clinical_text: Raw clinical note text

        Returns:
            Dictionary with entity types and extracted entities
        """
        if not clinical_text:
            return {}

        # Start with keyword-based extraction (always works)
        keyword_entities = self._simple_entity_extraction(clinical_text)
        
        try:
            if self.ner_pipeline is None:
                return keyword_entities

            # Run OpenMed NER for disease detection
            ner_results = self.ner_pipeline(clinical_text)

            # Combine OpenMed diseases with keyword results
            combined_entities = keyword_entities.copy()
            
            # Add OpenMed-detected diseases
            if ner_results:
                openmed_diseases = [entity['word'].strip() for entity in ner_results 
                                   if entity.get('entity_group') == 'DISEASE']
                
                if openmed_diseases:
                    # Merge with keyword-detected conditions
                    existing_conditions = combined_entities.get('conditions', [])
                    combined_entities['conditions'] = list(set(existing_conditions + openmed_diseases))

            return combined_entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            # Fallback to keyword extraction
            return keyword_entities

    def _simple_entity_extraction(self, text: str) -> Dict[str, List[str]]:
        """Fallback simple keyword-based extraction optimized for Synthea notes"""
        import re

        # Comprehensive medical keywords (Synthea-optimized)
        conditions = [
            # Chronic diseases
            'diabetes', 'diabetes mellitus', 'dm2', 'diabetic',
            'hypertension', 'htn', 'high blood pressure', 'elevated blood pressure',
            'copd', 'chronic obstructive', 'emphysema',
            'chf', 'heart failure', 'congestive heart failure', 'cardiac failure',
            'chronic kidney', 'ckd', 'renal disease', 'renal failure', 'kidney disease',
            
            # Acute conditions
            'mi', 'myocardial infarction', 'heart attack',
            'stroke', 'cerebrovascular', 'cva',
            'pneumonia', 'lung infection',
            'sepsis', 'septic', 'septicemia',
            'uti', 'urinary tract infection',
            
            # Cancers
            'cancer', 'malignancy', 'carcinoma', 'tumor', 'neoplasm',
            
            # Common Synthea conditions
            'gingivitis', 'gingival disease', 'periodontal',
            'asthma', 'reactive airway',
            'obesity', 'overweight', 'bmi',
            'depression', 'anxiety', 'mental health',
            'arthritis', 'osteoarthritis', 'joint pain',
            'anemia', 'iron deficiency',
            'hyperlipidemia', 'high cholesterol', 'dyslipidemia',
        ]
        
        medications = [
            # Diabetes medications
            'aspirin', 'metformin', 'insulin', 'glipizide', 'glyburide',
            
            # Cardiovascular medications
            'lisinopril', 'enalapril', 'ramipril', 'ace inhibitor',
            'atorvastatin', 'simvastatin', 'statin', 'lipitor',
            'metoprolol', 'atenolol', 'beta blocker', 'carvedilol',
            'amlodipine', 'calcium channel blocker',
            
            # Anticoagulants
            'warfarin', 'heparin', 'apixaban', 'rivaroxaban',
            
            # Diuretics
            'furosemide', 'lasix', 'hydrochlorothiazide', 'hctz',
            
            # Common Synthea medications
            'ibuprofen', 'acetaminophen', 'tylenol',
            'amoxicillin', 'antibiotic',
        ]
        
        symptoms = [
            'pain', 'ache', 'discomfort', 'soreness',
            'dyspnea', 'shortness of breath', 'sob', 'difficulty breathing',
            'fatigue', 'tired', 'weakness',
            'nausea', 'vomiting', 'emesis',
            'fever', 'elevated temperature',
            'cough', 'productive cough',
            'edema', 'swelling',
            'dizziness', 'lightheaded',
        ]

        text_lower = text.lower()

        found_entities = {
            'conditions': [c for c in conditions if c in text_lower],
            'medications': [m for m in medications if m in text_lower],
            'symptoms': [s for s in symptoms if s in text_lower],
        }

        return {k: v for k, v in found_entities.items() if v}

    def extract_medical_entities_batch(self, clinical_texts: List[str], batch_size: int = 32) -> List[Dict[str, List[str]]]:
        """
        Batch process multiple clinical texts for GPU efficiency
        """
        results = []
        
        # 1. Simple regex extraction (very fast)
        regex_results = [self._simple_entity_extraction(text) for text in clinical_texts]
        
        if self.ner_pipeline is None:
            return regex_results
            
        try:
            # 2. Batch NER processing
            # Proceed only for non-empty texts to save compute
            valid_indices = [i for i, t in enumerate(clinical_texts) if t and t.strip()]
            valid_texts = [clinical_texts[i] for i in valid_indices]
            
            if not valid_texts:
                return regex_results

            logger.info(f"Running NER on {len(valid_texts)} texts with batch_size={batch_size}...")
            
            # Using pipeline as iterator
            ner_iterator = self.ner_pipeline(valid_texts, batch_size=batch_size)
            
            # Map valid results back to original indices
            ner_map = {}
            for idx, ner_result in zip(valid_indices, ner_iterator):
                diseases = [
                    entity['word'].strip() 
                    for entity in ner_result 
                    if entity.get('entity_group') == 'DISEASE'
                ]
                ner_map[idx] = diseases
                
            # 3. Merge results
            for i in range(len(clinical_texts)):
                merged = regex_results[i].copy()
                if i in ner_map and ner_map[i]:
                    existing = merged.get('conditions', [])
                    merged['conditions'] = list(set(existing + ner_map[i]))
                results.append(merged)
                
            return results

        except Exception as e:
            logger.error(f"Batch extraction failed: {str(e)}")
            return regex_results