#!/usr/bin/env python3
"""
Detect real readmissions from Synthea encounter data in PostgreSQL
A readmission = patient returns within 30 days of previous discharge
"""

import pandas as pd
from sqlalchemy import create_engine
from datetime import timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DB_URI = "postgresql://postgres:qwerty@localhost:5433/healthflow_fhir"

def detect_readmissions():
    """
    Query PostgreSQL to detect readmissions from encounter data
    """
    logger.info("🔍 Analyzing encounter data for readmissions...")
    
    engine = create_engine(DB_URI)
    
    # SQL query to detect readmissions from FHIR bundles
    query = """
    WITH encounters_raw AS (
        SELECT 
            patient_id,
            jsonb_array_elements(bundle_data::jsonb->'entry') as entry
        FROM fhir_bundles
    ),
    encounters_parsed AS (
        SELECT 
            patient_id,
            entry->'resource'->>'id' as encounter_id,
            (entry->'resource'->'period'->>'start')::timestamp as start_date,
            (entry->'resource'->'period'->>'end')::timestamp as end_date,
            entry->'resource'->>'class' as encounter_class
        FROM encounters_raw
        WHERE entry->'resource'->>'resourceType' = 'Encounter'
        AND entry->'resource'->'period'->>'end' IS NOT NULL
        AND entry->'resource'->'period'->>'start' IS NOT NULL
        AND (
            entry->'resource'->>'class' LIKE '%inpatient%' 
            OR entry->'resource'->>'class' LIKE '%emergency%'
            OR entry->'resource'->>'class' LIKE '%ambulatory%'
        )
    ),
    ordered_encounters AS (
        SELECT 
            patient_id,
            encounter_id,
            start_date as admission,
            end_date as discharge,
            encounter_class,
            LAG(end_date) OVER (
                PARTITION BY patient_id 
                ORDER BY end_date
            ) as previous_discharge
        FROM encounters_parsed
    )
    SELECT 
        patient_id,
        encounter_id,
        admission,
        discharge,
        previous_discharge,
        CASE 
            WHEN previous_discharge IS NOT NULL 
            AND admission - previous_discharge <= interval '30 days'
            THEN 1
            ELSE 0
        END as is_readmission_30d,
        EXTRACT(days FROM (admission - previous_discharge)) as days_since_last_discharge
    FROM ordered_encounters
    WHERE discharge IS NOT NULL
    ORDER BY patient_id, admission;
    """
    
    try:
        logger.info("Executing SQL query...")
        df = pd.read_sql(query, engine)
        logger.info(f"✅ Loaded {len(df)} encounters")
    except Exception as e:
        logger.error(f"❌ SQL Error: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None
        
        # Statistics
        total_encounters = len(df)
        readmissions = df['is_readmission_30d'].sum()
        readmission_rate = (readmissions / total_encounters * 100) if total_encounters > 0 else 0
        
        logger.info(f"\n📊 Readmission Statistics:")
        logger.info(f"   Total encounters: {total_encounters}")
        logger.info(f"   Readmissions (30d): {readmissions}")
        logger.info(f"   Readmission rate: {readmission_rate:.1f}%")
        
        if readmissions > 0:
            logger.info(f"\n✅ REAL readmissions detected in data!")
            logger.info(f"   Avg days between admissions: {df[df['is_readmission_30d']==1]['days_since_last_discharge'].mean():.1f}")
            
            # Save readmission labels
            patient_labels = df.groupby('patient_id').agg({
                'is_readmission_30d': 'max'  # 1 if patient had any readmission
            }).reset_index()
            patient_labels.columns = ['patient_id', 'label_readmission']
            
            logger.info(f"\n💾 Saving readmission labels for {len(patient_labels)} patients...")
            patient_labels.to_csv('../patient_readmission_labels.csv', index=False)
            
            return patient_labels
        else:
            logger.warning(f"\n⚠️ No readmissions found in data")
            logger.info(f"   This is normal for Synthea - it doesn't simulate readmissions")
            logger.info(f"   Recommendation: Use synthetic labels based on risk factors")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None
    finally:
        engine.dispose()

if __name__ == "__main__":
    labels = detect_readmissions()
    
    if labels is not None:
        print(f"\n🎉 Success! Readmission labels saved to patient_readmission_labels.csv")
        print(f"   Merge with your dataset using patient_id")
    else:
        print(f"\n💡 No real readmissions found. Use generate_labels.py instead.")
