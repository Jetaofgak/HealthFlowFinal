#!/usr/bin/env python3
"""
Memory-optimized parallel FHIR data loader
Uses multiprocessing with controlled memory usage
"""

import json
import os
import sys
import base64
import gc
from pathlib import Path
from typing import List, Dict, Iterator
import psycopg2
from psycopg2.extras import execute_batch
from multiprocessing import Pool, cpu_count
from functools import partial

# Memory optimization settings
MEMORY_CONFIG = {
    'batch_size': 20,        # Files per batch insert (was 50)
    'chunk_size': 2,         # Files per worker chunk (was 5)
    'max_workers': 6,        # Maximum parallel workers (was cpu_count)
    'min_workers': 4,        # Minimum parallel workers
    'progress_interval': 50  # Show progress every N files
}

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
    """Process a single FHIR JSON file (worker function) - memory optimized"""
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

        # Extract clinical notes before storing bundle
        notes = extract_clinical_notes(bundle)

        # Convert bundle to JSON string immediately to reduce object overhead
        bundle_json = json.dumps(bundle)

        # Clear the bundle dict from memory
        del bundle

        return {
            'patient_id': patient_id,
            'bundle_json': bundle_json,  # Store as string, not dict
            'notes': notes
        }

    except Exception as e:
        return None

def load_fhir_files_parallel(conn, fhir_dir: str, num_workers: int = None):
    """Load FHIR files in parallel using multiprocessing with optimized memory usage"""
    fhir_path = Path(fhir_dir)

    # Use iterator to avoid loading all paths at once
    json_files_iter = fhir_path.glob('*.json')
    json_files = list(json_files_iter)  # Still need count for progress

    if not json_files:
        print(f"❌ No JSON files found in {fhir_dir}")
        return

    total_files = len(json_files)
    print(f"📂 Found {total_files} FHIR bundle files")

    # Memory optimization: Use fewer workers (4-6 instead of all cores)
    if num_workers is None:
        num_workers = min(6, max(4, cpu_count() // 2))

    print(f"🚀 Using {num_workers} parallel workers (memory-optimized)")

    cursor = conn.cursor()
    total_notes_count = 0
    processed_count = 0

    # Reduced batch size for lower memory footprint
    batch_size = 20
    batch_results = []

    # Process files in parallel with smaller chunks
    with Pool(num_workers) as pool:
        # Reduced chunksize from 5 to 2 for better memory distribution
        for result in pool.imap_unordered(process_file, json_files, chunksize=2):
            if result:
                batch_results.append(result)

            processed_count += 1

            # Insert batch when full
            if len(batch_results) >= batch_size:
                _insert_batch(cursor, batch_results)
                conn.commit()
                total_notes_count += sum(len(r['notes']) for r in batch_results)

                # Explicit memory cleanup
                batch_results.clear()
                gc.collect()

                # Progress update every 50 files
                if processed_count % 50 == 0:
                    print(f"   Processed {processed_count}/{total_files} files... ({processed_count*100//total_files}%)")

        # Insert remaining items
        if batch_results:
            _insert_batch(cursor, batch_results)
            conn.commit()
            total_notes_count += sum(len(r['notes']) for r in batch_results)
            batch_results.clear()
            gc.collect()

    print(f"✅ Parallel processing complete. Total clinical notes inserted: {total_notes_count}")

def _insert_batch(cursor, results):
    """Helper to insert a batch of results - memory optimized"""
    # Prepare batch data for bundles
    bundle_data = [
        (result['patient_id'], result['bundle_json'])
        for result in results
    ]

    # Batch insert bundles for better performance
    execute_batch(
        cursor,
        "INSERT INTO fhir_bundles (patient_id, bundle_data) VALUES (%s, %s)",
        bundle_data
    )

    # Insert all notes in one batch
    all_notes = []
    for result in results:
        all_notes.extend(result['notes'])

    if all_notes:
        execute_batch(
            cursor,
            """
            INSERT INTO clinical_notes
            (patient_id, encounter_id, note_date, note_type, note_text)
            VALUES (%(patient_id)s, %(encounter_id)s, %(note_date)s,
                    %(note_type)s, %(note_text)s)
            """,
            all_notes
        )

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
