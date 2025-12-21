#!/usr/bin/env python3
"""
Load Synthea FHIR data into PostgreSQL database
Extracts clinical notes from DocumentReference resources
"""

import json
import os
import sys
import base64
from pathlib import Path
from typing import List, Dict
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'healthflow_fhir',
    'user': 'postgres',
    'password': 'qwerty'
}

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to database")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def create_tables(conn):
    """Create tables for storing FHIR data and clinical notes"""
    cursor = conn.cursor()
    
    # Table for clinical notes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinical_notes (
            id SERIAL PRIMARY KEY,
            patient_id VARCHAR(255) NOT NULL,
            encounter_id VARCHAR(255),
            note_date TIMESTAMP,
            note_type VARCHAR(100),
            note_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_clinical_notes_patient 
        ON clinical_notes(patient_id);
    """)
    
    # Table for raw FHIR bundles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fhir_bundles (
            id SERIAL PRIMARY KEY,
            patient_id VARCHAR(255) NOT NULL,
            bundle_data JSONB NOT NULL,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_fhir_bundles_patient 
        ON fhir_bundles(patient_id);
    """)
    
    conn.commit()
    print("✅ Tables created/verified")

def extract_clinical_notes(bundle: Dict) -> List[Dict]:
    """Extract clinical notes from FHIR bundle"""
    notes = []
    patient_id = None
    
    # Find patient ID
    for entry in bundle.get('entry', []):
        resource = entry.get('resource', {})
        if resource.get('resourceType') == 'Patient':
            patient_id = resource.get('id')
            break
    
    if not patient_id:
        return notes
    
    # Extract DocumentReference resources (clinical notes)
    for entry in bundle.get('entry', []):
        resource = entry.get('resource', {})
        
        if resource.get('resourceType') == 'DocumentReference':
            note_id = resource.get('id')
            note_date = resource.get('date')
            note_type = resource.get('type', {}).get('text', 'Clinical Note')
            
            # Extract note content
            for content in resource.get('content', []):
                attachment = content.get('attachment', {})
                
                # Decode base64 content
                if 'data' in attachment:
                    try:
                        note_text = base64.b64decode(attachment['data']).decode('utf-8')
                        
                        notes.append({
                            'patient_id': patient_id,
                            'encounter_id': note_id,
                            'note_date': note_date,
                            'note_type': note_type,
                            'note_text': note_text
                        })
                    except Exception as e:
                        print(f"⚠️  Failed to decode note: {e}")
    
    return notes

def load_fhir_files(conn, fhir_dir: str):
    """Load all FHIR JSON files from directory"""
    fhir_path = Path(fhir_dir)
    json_files = list(fhir_path.glob('*.json'))
    
    if not json_files:
        print(f"❌ No JSON files found in {fhir_dir}")
        return
    
    print(f"📂 Found {len(json_files)} FHIR bundle files")
    
    cursor = conn.cursor()
    total_notes = 0
    
    for i, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r') as f:
                bundle = json.load(f)
            
            # Extract patient ID
            patient_id = None
            for entry in bundle.get('entry', []):
                resource = entry.get('resource', {})
                if resource.get('resourceType') == 'Patient':
                    patient_id = resource.get('id')
                    break
            
            if not patient_id:
                continue
            
            # Store raw bundle
            cursor.execute(
                "INSERT INTO fhir_bundles (patient_id, bundle_data) VALUES (%s, %s)",
                (patient_id, json.dumps(bundle))
            )
            
            # Extract and store clinical notes
            notes = extract_clinical_notes(bundle)
            
            if notes:
                execute_batch(
                    cursor,
                    """
                    INSERT INTO clinical_notes 
                    (patient_id, encounter_id, note_date, note_type, note_text)
                    VALUES (%(patient_id)s, %(encounter_id)s, %(note_date)s, 
                            %(note_type)s, %(note_text)s)
                    """,
                    notes
                )
                total_notes += len(notes)
            
            if i % 100 == 0:
                conn.commit()
                print(f"   Processed {i}/{len(json_files)} files...")
        
        except Exception as e:
            print(f"⚠️  Error processing {json_file.name}: {e}")
            continue
    
    conn.commit()
    print(f"✅ Loaded {len(json_files)} patients with {total_notes} clinical notes")

def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python load_synthea_to_db.py <synthea_fhir_directory>")
        print("Example: python load_synthea_to_db.py synthea_output/fhir")
        sys.exit(1)
    
    fhir_dir = sys.argv[1]
    
    if not os.path.exists(fhir_dir):
        print(f"❌ Directory not found: {fhir_dir}")
        sys.exit(1)
    
    print("🏥 HealthFlow-MS: Load Synthea Data to PostgreSQL")
    print("=" * 50)
    
    conn = connect_db()
    create_tables(conn)
    load_fhir_files(conn, fhir_dir)
    
    # Show statistics
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fhir_bundles")
    patient_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM clinical_notes")
    note_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(LENGTH(note_text)) FROM clinical_notes")
    avg_note_length = cursor.fetchone()[0]
    
    print("\n📊 Database Statistics:")
    print(f"   Patients loaded: {patient_count}")
    print(f"   Clinical notes: {note_count}")
    print(f"   Avg note length: {int(avg_note_length) if avg_note_length else 0} characters")
    
    conn.close()
    print("\n🎉 Data loading complete!")

if __name__ == '__main__':
    main()
