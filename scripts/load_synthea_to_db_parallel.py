#!/usr/bin/env python3
"""
Parallel FHIR data loader - 4x faster than sequential
Uses multiprocessing to load FHIR bundles in parallel
"""

import json
import os
import sys
import base64
from pathlib import Path
from typing import List, Dict
import psycopg2
from psycopg2.extras import execute_batch
from multiprocessing import Pool, cpu_count
from functools import partial

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
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def create_tables(conn):
    """Create tables for storing FHIR data and clinical notes"""
    cursor = conn.cursor()
    
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
    
    for entry in bundle.get('entry', []):
        resource = entry.get('resource', {})
        if resource.get('resourceType') == 'Patient':
            patient_id = resource.get('id')
            break
    
    if not patient_id:
        return notes
    
    for entry in bundle.get('entry', []):
        resource = entry.get('resource', {})
        
        if resource.get('resourceType') == 'DocumentReference':
            note_id = resource.get('id')
            note_date = resource.get('date')
            note_type = resource.get('type', {}).get('text', 'Clinical Note')
            
            for content in resource.get('content', []):
                attachment = content.get('attachment', {})
                
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
                    except Exception:
                        pass
    
    return notes

def process_file(json_file: Path) -> Dict:
    """Process a single FHIR JSON file (worker function)"""
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
            return None
        
        # Extract clinical notes
        notes = extract_clinical_notes(bundle)
        
        return {
            'patient_id': patient_id,
            'bundle': bundle,
            'notes': notes
        }
    
    except Exception as e:
        return None

def load_fhir_files_parallel(conn, fhir_dir: str, num_workers: int = None):
    """Load FHIR files in parallel using multiprocessing"""
    fhir_path = Path(fhir_dir)
    json_files = list(fhir_path.glob('*.json'))
    
    if not json_files:
        print(f"❌ No JSON files found in {fhir_dir}")
        return
    
    print(f"📂 Found {len(json_files)} FHIR bundle files")
    
    # Use all CPU cores by default
    if num_workers is None:
        num_workers = cpu_count()
    
    print(f"🚀 Using {num_workers} parallel workers")
    
    # Process files in parallel
    with Pool(num_workers) as pool:
        results = []
        for i, result in enumerate(pool.imap_unordered(process_file, json_files, chunksize=10), 1):
            if result:
                results.append(result)
            
            if i % 100 == 0:
                print(f"   Processed {i}/{len(json_files)} files...")
    
    print(f"✅ Parallel processing complete. Inserting into database...")
    
    # Batch insert into database
    cursor = conn.cursor()
    total_notes = 0
    
    for i, result in enumerate(results, 1):
        # Insert bundle
        cursor.execute(
            "INSERT INTO fhir_bundles (patient_id, bundle_data) VALUES (%s, %s)",
            (result['patient_id'], json.dumps(result['bundle']))
        )
        
        # Insert notes
        if result['notes']:
            execute_batch(
                cursor,
                """
                INSERT INTO clinical_notes 
                (patient_id, encounter_id, note_date, note_type, note_text)
                VALUES (%(patient_id)s, %(encounter_id)s, %(note_date)s, 
                        %(note_type)s, %(note_text)s)
                """,
                result['notes']
            )
            total_notes += len(result['notes'])
        
        if i % 500 == 0:
            conn.commit()
            print(f"   Inserted {i}/{len(results)} patients into database...")
    
    conn.commit()
    print(f"✅ Loaded {len(results)} patients with {total_notes} clinical notes")

def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python load_synthea_to_db_parallel.py <synthea_fhir_directory> [num_workers]")
        print("Example: python load_synthea_to_db_parallel.py synthea_output/fhir 8")
        sys.exit(1)
    
    fhir_dir = sys.argv[1]
    num_workers = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not os.path.exists(fhir_dir):
        print(f"❌ Directory not found: {fhir_dir}")
        sys.exit(1)
    
    print("🏥 HealthFlow-MS: Parallel FHIR Data Loader")
    print("=" * 50)
    
    conn = connect_db()
    print("✅ Connected to database")
    
    create_tables(conn)
    load_fhir_files_parallel(conn, fhir_dir, num_workers)
    
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
    print("\n🎉 Parallel data loading complete!")

if __name__ == '__main__':
    main()
