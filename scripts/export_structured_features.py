#!/usr/bin/env python3
"""
Export Structured Features from PostgreSQL
Extracts structured patient features from FHIR data in PostgreSQL
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import logging
from datetime import datetime
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_URI = "postgresql://postgres:qwerty@localhost:5433/healthflow_fhir"


class StructuredFeatureExtractor:
    """Extract structured features from FHIR bundles in PostgreSQL"""
    
    def __init__(self, engine):
        self.engine = engine
    
    def extract_patient_demographics(self, bundle: Dict) -> Dict:
        """Extract demographic features from FHIR bundle"""
        features = {}
        
        # Find Patient resource
        patient = self._find_resource(bundle, 'Patient')
        if not patient:
            return self._empty_demographics()
        
        # Age calculation
        birth_date = patient.get('birthDate')
        if birth_date:
            birth_year = int(birth_date.split('-')[0])
            current_year = datetime.now().year
            features['age'] = current_year - birth_year
        else:
            features['age'] = 0
        
        # Gender
        gender = patient.get('gender', 'unknown')
        features['gender_male'] = 1 if gender == 'male' else 0
        features['gender_female'] = 1 if gender == 'female' else 0
        
        # Race and ethnicity (from extensions)
        extensions = patient.get('extension', [])
        features['race_white'] = 0
        features['race_black'] = 0
        features['race_asian'] = 0
        features['ethnicity_hispanic'] = 0
        
        for ext in extensions:
            url = ext.get('url', '')
            if 'race' in url.lower():
                value = ext.get('valueString', '').lower()
                if 'white' in value:
                    features['race_white'] = 1
                elif 'black' in value or 'african' in value:
                    features['race_black'] = 1
                elif 'asian' in value:
                    features['race_asian'] = 1
            elif 'ethnicity' in url.lower():
                value = ext.get('valueString', '').lower()
                if 'hispanic' in value or 'latino' in value:
                    features['ethnicity_hispanic'] = 1
        
        return features
    
    def extract_vital_signs(self, bundle: Dict) -> Dict:
        """Extract vital signs from Observation resources"""
        features = {
            'vit_sys_bp': 0,
            'vit_dia_bp': 0,
            'vit_heart_rate': 0,
            'vit_resp_rate': 0,
            'vit_temp': 0,
            'vit_weight': 0,
            'vit_height': 0,
            'vit_bmi': 0,
        }
        
        observations = self._find_all_resources(bundle, 'Observation')
        
        for obs in observations:
            code = self._get_code_text(obs.get('code', {}))
            value = self._get_observation_value(obs)
            
            if not value:
                continue
            
            code_lower = code.lower()
            
            if 'systolic' in code_lower or 'blood pressure systolic' in code_lower:
                features['vit_sys_bp'] = value
            elif 'diastolic' in code_lower or 'blood pressure diastolic' in code_lower:
                features['vit_dia_bp'] = value
            elif 'heart rate' in code_lower or 'pulse' in code_lower:
                features['vit_heart_rate'] = value
            elif 'respiratory rate' in code_lower:
                features['vit_resp_rate'] = value
            elif 'body temperature' in code_lower:
                features['vit_temp'] = value
            elif 'body weight' in code_lower:
                features['vit_weight'] = value
            elif 'body height' in code_lower:
                features['vit_height'] = value
            elif 'body mass index' in code_lower or 'bmi' in code_lower:
                features['vit_bmi'] = value
        
        return features
    
    def extract_conditions(self, bundle: Dict) -> Dict:
        """Extract condition/diagnosis features"""
        features = {
            'cond_diabetes': 0,
            'cond_hypertension': 0,
            'cond_chf': 0,
            'cond_copd': 0,
            'cond_ckd': 0,
            'cond_cancer': 0,
            'num_conditions': 0,
        }
        
        conditions = self._find_all_resources(bundle, 'Condition')
        features['num_conditions'] = len(conditions)
        
        for condition in conditions:
            code_text = self._get_code_text(condition.get('code', {})).lower()
            
            if 'diabetes' in code_text:
                features['cond_diabetes'] = 1
            if 'hypertension' in code_text or 'high blood pressure' in code_text:
                features['cond_hypertension'] = 1
            if 'heart failure' in code_text or 'chf' in code_text:
                features['cond_chf'] = 1
            if 'copd' in code_text or 'chronic obstructive' in code_text:
                features['cond_copd'] = 1
            if 'chronic kidney' in code_text or 'ckd' in code_text or 'renal' in code_text:
                features['cond_ckd'] = 1
            if 'cancer' in code_text or 'malignancy' in code_text:
                features['cond_cancer'] = 1
        
        return features
    
    def extract_medications(self, bundle: Dict) -> Dict:
        """Extract medication features"""
        features = {
            'med_insulin': 0,
            'med_metformin': 0,
            'med_statin': 0,
            'med_ace_inhibitor': 0,
            'med_beta_blocker': 0,
            'num_medications': 0,
            'polypharmacy': 0,
        }
        
        medications = self._find_all_resources(bundle, 'MedicationRequest')
        features['num_medications'] = len(medications)
        features['polypharmacy'] = 1 if len(medications) >= 5 else 0
        
        for med in medications:
            code_text = self._get_code_text(med.get('medicationCodeableConcept', {})).lower()
            
            if 'insulin' in code_text:
                features['med_insulin'] = 1
            if 'metformin' in code_text:
                features['med_metformin'] = 1
            if 'statin' in code_text or 'atorvastatin' in code_text or 'simvastatin' in code_text:
                features['med_statin'] = 1
            if 'lisinopril' in code_text or 'enalapril' in code_text or 'ace inhibitor' in code_text:
                features['med_ace_inhibitor'] = 1
            if 'metoprolol' in code_text or 'atenolol' in code_text or 'beta blocker' in code_text:
                features['med_beta_blocker'] = 1
        
        return features
    
    def extract_lab_results(self, bundle: Dict) -> Dict:
        """Extract laboratory test results"""
        features = {
            'lab_glucose': 0,
            'lab_hba1c': 0,
            'lab_creatinine': 0,
            'lab_cholesterol': 0,
            'lab_ldl': 0,
            'lab_hdl': 0,
        }
        
        observations = self._find_all_resources(bundle, 'Observation')
        
        for obs in observations:
            code = self._get_code_text(obs.get('code', {})).lower()
            value = self._get_observation_value(obs)
            
            if not value:
                continue
            
            if 'glucose' in code:
                features['lab_glucose'] = value
            elif 'hemoglobin a1c' in code or 'hba1c' in code:
                features['lab_hba1c'] = value
            elif 'creatinine' in code:
                features['lab_creatinine'] = value
            elif 'cholesterol' in code and 'ldl' not in code and 'hdl' not in code:
                features['lab_cholesterol'] = value
            elif 'ldl' in code:
                features['lab_ldl'] = value
            elif 'hdl' in code:
                features['lab_hdl'] = value
        
        return features
    
    def extract_all_features(self, patient_id: str, bundle_data) -> Dict:
        """Extract all structured features from a FHIR bundle"""
        import json
        
        try:
            # Handle both string and dict types
            if isinstance(bundle_data, str):
                bundle = json.loads(bundle_data)
            elif isinstance(bundle_data, dict):
                bundle = bundle_data
            else:
                logger.error(f"Invalid bundle_data type for {patient_id}: {type(bundle_data)}")
                return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {patient_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing bundle for {patient_id}: {e}")
            return None
        
        features = {'patient_id': patient_id}
        
        # Extract all feature categories
        features.update(self.extract_patient_demographics(bundle))
        features.update(self.extract_vital_signs(bundle))
        features.update(self.extract_conditions(bundle))
        features.update(self.extract_medications(bundle))
        features.update(self.extract_lab_results(bundle))
        
        return features
    
    # Helper methods
    def _find_resource(self, bundle: Dict, resource_type: str) -> Dict:
        """Find first resource of given type in bundle"""
        for entry in bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == resource_type:
                return resource
        return {}
    
    def _find_all_resources(self, bundle: Dict, resource_type: str) -> List[Dict]:
        """Find all resources of given type in bundle"""
        resources = []
        for entry in bundle.get('entry', []):
            resource = entry.get('resource', {})
            if resource.get('resourceType') == resource_type:
                resources.append(resource)
        return resources
    
    def _get_code_text(self, code_obj: Dict) -> str:
        """Extract text from CodeableConcept"""
        if 'text' in code_obj:
            return code_obj['text']
        
        codings = code_obj.get('coding', [])
        if codings:
            return codings[0].get('display', '')
        
        return ''
    
    def _get_observation_value(self, observation: Dict) -> float:
        """Extract numeric value from Observation"""
        if 'valueQuantity' in observation:
            return float(observation['valueQuantity'].get('value', 0))
        return 0
    
    def _empty_demographics(self) -> Dict:
        """Return empty demographics dict"""
        return {
            'age': 0,
            'gender_male': 0,
            'gender_female': 0,
            'race_white': 0,
            'race_black': 0,
            'race_asian': 0,
            'ethnicity_hispanic': 0,
        }


def main():
    """Main execution"""
    logger.info("🏥 Structured Feature Extraction from PostgreSQL")
    logger.info("=" * 50)
    
    OUTPUT_CSV = "../dataset_structured.csv"  # Fixed name - no need to update train.py
    
    try:
        # Connect to database
        logger.info("Connecting to PostgreSQL...")
        engine = create_engine(DB_URI)
        
        # Load FHIR bundles
        logger.info("Loading FHIR bundles from database...")
        query = "SELECT patient_id, bundle_data FROM fhir_bundles ORDER BY patient_id"
        bundles_df = pd.read_sql(query, engine)
        logger.info(f"Loaded {len(bundles_df)} FHIR bundles")
        
        # Extract features
        logger.info("Extracting structured features...")
        extractor = StructuredFeatureExtractor(engine)
        
        features_list = []
        failed_count = 0
        
        for idx, row in bundles_df.iterrows():
            try:
                features = extractor.extract_all_features(row['patient_id'], row['bundle_data'])
                if features:
                    features_list.append(features)
                else:
                    failed_count += 1
                    if failed_count <= 3:  # Show first 3 failures
                        logger.warning(f"Failed to extract features for patient {row['patient_id']}")
            except Exception as e:
                failed_count += 1
                if failed_count <= 3:
                    logger.error(f"Error processing patient {row['patient_id']}: {e}")
        
        if failed_count > 0:
            logger.warning(f"Failed to process {failed_count} patients")
        
        # Create DataFrame
        features_df = pd.DataFrame(features_list)
        logger.info(f"Extracted features for {len(features_df)} patients")
        
        # Save to CSV
        logger.info(f"Saving to {OUTPUT_CSV}...")
        features_df.to_csv(OUTPUT_CSV, index=False)
        
        # Show statistics
        logger.info("\n📊 Dataset Statistics:")
        logger.info(f"   Total patients: {len(features_df)}")
        logger.info(f"   Total features: {len(features_df.columns)}")
        logger.info(f"\n📝 Sample Features (first patient):")
        for col in list(features_df.columns)[:10]:
            logger.info(f"   {col}: {features_df[col].iloc[0]}")
        
        logger.info("\n🎉 Feature extraction complete!")
        logger.info(f"✅ Structured dataset saved to: {OUTPUT_CSV}")
        logger.info(f"\n💡 Next step: Extract NLP features with:")
        logger.info(f"   python3 extract_biobert_features.py")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
