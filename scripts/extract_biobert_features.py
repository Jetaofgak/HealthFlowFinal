#!/usr/bin/env python3
"""
BioBERT Feature Extraction Script
Extracts NLP features from clinical notes and combines with structured features
"""

import sys
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from typing import Dict, List
import logging
from tqdm import tqdm

# Add featurizer to path to use BioBERT service
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'featurizer'))

from services.biobert_service import BioBERTService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_URI = "postgresql://postgres:qwerty@localhost:5433/healthflow_fhir"

class ClinicalNLPExtractor:
    """Extract NLP features from clinical notes using BioBERT"""
    
    def __init__(self):
        logger.info("Initializing BioBERT service...")
        self.biobert = BioBERTService()
        logger.info("BioBERT service loaded successfully")
    
    def extract_features_from_notes(self, notes: List[str]) -> Dict:
        """
        Extract NLP features from a list of clinical notes
        
        Args:
            notes: List of clinical note texts
            
        Returns:
            Dictionary of NLP-derived features
        """
        if not notes:
            return self._empty_features()
        
        # Combine all notes for the patient
        combined_text = " ".join([note for note in notes if note])
        
        if not combined_text.strip():
            return self._empty_features()
        
        # Extract medical entities using BioBERT
        entities = self.biobert.extract_medical_entities(combined_text)
        
        # Extract features from entities
        features = {
            # Comorbidity features
            'nlp_num_conditions': len(entities.get('conditions', [])),
            'nlp_has_chf': int(self._has_condition(entities, ['chf', 'heart failure', 'congestive'])),
            'nlp_has_copd': int(self._has_condition(entities, ['copd', 'chronic obstructive'])),
            'nlp_has_ckd': int(self._has_condition(entities, ['ckd', 'chronic kidney', 'renal'])),
            'nlp_has_diabetes': int(self._has_condition(entities, ['diabetes', 'dm2', 'diabetic'])),
            'nlp_has_hypertension': int(self._has_condition(entities, ['hypertension', 'htn', 'high blood pressure'])),
            
            # Medication features
            'nlp_num_medications': len(entities.get('medications', [])),
            'nlp_polypharmacy': int(len(entities.get('medications', [])) >= 5),
            
            # Complexity indicators
            'nlp_note_length': len(combined_text),
            'nlp_note_count': len(notes),
            'nlp_avg_note_length': len(combined_text) / len(notes) if notes else 0,
            
            # Symptom indicators
            'nlp_num_symptoms': len(entities.get('symptoms', [])),
            'nlp_has_pain': int(self._has_symptom(entities, ['pain', 'ache', 'discomfort'])),
            'nlp_has_dyspnea': int(self._has_symptom(entities, ['dyspnea', 'shortness of breath', 'sob'])),
        }
        
        return features
    
    def _has_condition(self, entities: Dict, keywords: List[str]) -> bool:
        """Check if any keyword appears in conditions"""
        conditions_text = ' '.join(entities.get('conditions', [])).lower()
        return any(keyword in conditions_text for keyword in keywords)
    
    def _has_symptom(self, entities: Dict, keywords: List[str]) -> bool:
        """Check if any keyword appears in symptoms"""
        symptoms_text = ' '.join(entities.get('symptoms', [])).lower()
        return any(keyword in symptoms_text for keyword in keywords)
    
    def _empty_features(self) -> Dict:
        """Return empty feature dict when no notes available"""
        return {
            'nlp_num_conditions': 0,
            'nlp_has_chf': 0,
            'nlp_has_copd': 0,
            'nlp_has_ckd': 0,
            'nlp_has_diabetes': 0,
            'nlp_has_hypertension': 0,
            'nlp_num_medications': 0,
            'nlp_polypharmacy': 0,
            'nlp_note_length': 0,
            'nlp_note_count': 0,
            'nlp_avg_note_length': 0,
            'nlp_num_symptoms': 0,
            'nlp_has_pain': 0,
            'nlp_has_dyspnea': 0,
        }


def load_clinical_notes(engine) -> pd.DataFrame:
    """Load clinical notes from database"""
    logger.info("Loading clinical notes from database...")
    
    query = """
    SELECT patient_id, note_text
    FROM clinical_notes
    ORDER BY patient_id, note_date
    """
    
    df = pd.read_sql(query, engine)
    logger.info(f"Loaded {len(df)} clinical notes for {df['patient_id'].nunique()} patients")
    
    return df


def load_structured_features(csv_path: str) -> pd.DataFrame:
    """Load existing structured features from CSV"""
    logger.info(f"Loading structured features from {csv_path}...")
    
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} records with {len(df.columns)} features")
    
    return df


def extract_nlp_features(notes_df: pd.DataFrame, extractor: ClinicalNLPExtractor) -> pd.DataFrame:
    """Extract NLP features for all patients"""
    logger.info("Extracting NLP features from clinical notes...")
    
    # Group notes by patient
    patient_notes = notes_df.groupby('patient_id')['note_text'].apply(list).reset_index()
    
    nlp_features_list = []
    
    for _, row in tqdm(patient_notes.iterrows(), total=len(patient_notes), desc="Processing patients"):
        patient_id = row['patient_id']
        notes = row['note_text']
        
        # Extract NLP features
        nlp_features = extractor.extract_features_from_notes(notes)
        nlp_features['patient_id'] = patient_id
        
        nlp_features_list.append(nlp_features)
    
    nlp_df = pd.DataFrame(nlp_features_list)
    logger.info(f"Extracted NLP features for {len(nlp_df)} patients")
    
    return nlp_df


def combine_features(structured_df: pd.DataFrame, nlp_df: pd.DataFrame) -> pd.DataFrame:
    """Combine structured and NLP features"""
    logger.info("Combining structured and NLP features...")
    
    # Merge on patient_id
    combined_df = structured_df.merge(nlp_df, on='patient_id', how='left')
    
    # Fill NaN values for patients without notes
    nlp_columns = [col for col in combined_df.columns if col.startswith('nlp_')]
    combined_df[nlp_columns] = combined_df[nlp_columns].fillna(0)
    
    logger.info(f"Combined dataset: {len(combined_df)} records, {len(combined_df.columns)} features")
    
    return combined_df


def main():
    """Main execution"""
    logger.info("🏥 BioBERT Feature Extraction Pipeline")
    logger.info("=" * 50)
    
    # Configuration - Fixed filenames
    STRUCTURED_CSV = "../dataset_structured.csv"  # From export_structured_features.py
    OUTPUT_CSV = "../dataset_with_nlp.csv"  # Final dataset for train.py
    
    try:
        # 1. Initialize BioBERT extractor
        extractor = ClinicalNLPExtractor()
        
        # 2. Connect to database
        logger.info("Connecting to PostgreSQL...")
        engine = create_engine(DB_URI)
        
        # 3. Load clinical notes
        notes_df = load_clinical_notes(engine)
        
        # 4. Load structured features
        structured_df = load_structured_features(STRUCTURED_CSV)
        
        # 5. Extract NLP features
        nlp_df = extract_nlp_features(notes_df, extractor)
        
        # 6. Combine features
        combined_df = combine_features(structured_df, nlp_df)
        
        # 7. Save enhanced dataset
        logger.info(f"Saving enhanced dataset to {OUTPUT_CSV}...")
        combined_df.to_csv(OUTPUT_CSV, index=False)
        
        # 8. Show statistics
        logger.info("\n📊 Dataset Statistics:")
        logger.info(f"   Total records: {len(combined_df)}")
        logger.info(f"   Structured features: {len([c for c in combined_df.columns if not c.startswith('nlp_')])}")
        logger.info(f"   NLP features: {len([c for c in combined_df.columns if c.startswith('nlp_')])}")
        logger.info(f"   Total features: {len(combined_df.columns)}")
        
        # Show sample NLP features
        nlp_cols = [c for c in combined_df.columns if c.startswith('nlp_')]
        logger.info(f"\n📝 Sample NLP Features (first patient):")
        for col in nlp_cols[:5]:
            logger.info(f"   {col}: {combined_df[col].iloc[0]}")
        
        logger.info("\n🎉 Feature extraction complete!")
        logger.info(f"✅ Enhanced dataset saved to: {OUTPUT_CSV}")
        logger.info(f"\n💡 Next step: Retrain XGBoost model with:")
        logger.info(f"   python train.py  # Update CSV_PATH to '{OUTPUT_CSV}'")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
