#!/usr/bin/env python3
"""
Ultra-fast SQL-based FHIR data loader (Parallel Version)
Uses Multiprocessing (4 cores) + PostgreSQL COPY + JSON functions
"""

import os
import sys
import psycopg2
from psycopg2 import extras
from pathlib import Path
import multiprocessing
import time

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

def create_tables_and_staging(conn):
    """Create tables and shared staging area"""
    cursor = conn.cursor()
    print("📋 Creating tables and staging area...")

    # Main tables
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
        CREATE INDEX IF NOT EXISTS idx_clinical_notes_patient ON clinical_notes(patient_id);
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fhir_bundles (
            id SERIAL PRIMARY KEY,
            patient_id VARCHAR(255) NOT NULL,
            bundle_data JSONB NOT NULL,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_fhir_bundles_patient ON fhir_bundles(patient_id);
    """)

    # Shared Staging Table (UNLOGGED for speed, but visible to all sessions)
    cursor.execute("""
        DROP TABLE IF EXISTS json_staging;
        CREATE UNLOGGED TABLE json_staging (
            file_path TEXT,
            bundle_data TEXT
        );
    """)
    conn.commit()
    print("✅ Tables ready")

def worker_load_batch(file_batch):
    """Worker function to load a batch of files"""
    try:
        # Each worker needs its own connection
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        values = []
        for json_file in file_batch:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    values.append((str(json_file), f.read()))
            except Exception as e:
                print(f"⚠️  Skipped {json_file}: {e}")

        if values:
            extras.execute_values(
                cursor,
                "INSERT INTO json_staging (file_path, bundle_data) VALUES %s",
                values,
                template="(%s, %s)"
            )
            conn.commit()
        
        conn.close()
        return len(values)
    except Exception as e:
        print(f"❌ Worker error: {e}")
        return 0

def bulk_load_json_parallel(conn, fhir_dir: str):
    """Parallel load controller"""
    fhir_path = Path(fhir_dir)
    json_files = list(fhir_path.glob('*.json'))

    if not json_files:
        print(f"❌ No JSON files found in {fhir_dir}")
        return

    total_files = len(json_files)
    print(f"📂 Found {total_files} FHIR bundle files")
    
    # 4 Cores recommended by user
    num_processes = 4
    print(f"🚀 Starting Parallel Load on {num_processes} cores...")
    
    # Split into chunks
    chunk_size = 250 # Adjust chunk size as needed
    chunks = [json_files[i:i + chunk_size] for i in range(0, total_files, chunk_size)]
    
    start_time = time.time()
    
    # Run workers
    processed = 0
    with multiprocessing.Pool(processes=num_processes) as pool:
        for batch_count in pool.imap_unordered(worker_load_batch, chunks):
            processed += batch_count
            if processed % 1000 == 0 or processed == total_files:
                print(f"      Staged {processed}/{total_files} files... ({processed*100//total_files}%)")
    
    print(f"✅ Staged {processed} files in {time.time() - start_time:.2f}s")
    
    # Final SQL Processing
    print("🔄 Processing staged data (SQL Extraction)...")
    cursor = conn.cursor()
    
    # Extract Bundles
    cursor.execute("""
        INSERT INTO fhir_bundles (patient_id, bundle_data)
        SELECT
            (patient_entry.resource->>'id')::varchar(255) as patient_id,
            bundle_data::jsonb
        FROM json_staging,
        LATERAL (
            SELECT jsonb_array_elements(bundle_data::jsonb->'entry') as entry
        ) entries,
        LATERAL (
            SELECT entry->'resource' as resource
            WHERE (entry->'resource'->>'resourceType') = 'Patient'
        ) patient_entry
        WHERE (patient_entry.resource->>'id') IS NOT NULL
    """)
    bundles_inserted = cursor.rowcount
    print(f"✅ Inserted {bundles_inserted} FHIR bundles")

    # Extract Notes
    cursor.execute("""
        INSERT INTO clinical_notes (patient_id, encounter_id, note_date, note_type, note_text)
        SELECT
            patient_id,
            doc_entry.resource->>'id' as encounter_id,
            (doc_entry.resource->>'date')::timestamp as note_date,
            COALESCE(doc_entry.resource->'type'->>'text', 'Clinical Note') as note_type,
            convert_from(decode(content->'attachment'->>'data', 'base64'), 'UTF8') as note_text
        FROM (
            SELECT
                (patient_entry.resource->>'id')::varchar(255) as patient_id,
                bundle_data
            FROM json_staging,
            LATERAL (
                SELECT jsonb_array_elements(bundle_data::jsonb->'entry') as entry
            ) entries,
            LATERAL (
                SELECT entry->'resource' as resource
                WHERE (entry->'resource'->>'resourceType') = 'Patient'
            ) patient_entry
            WHERE (patient_entry.resource->>'id') IS NOT NULL
        ) patients,
        LATERAL (
            SELECT jsonb_array_elements(bundle_data::jsonb->'entry') as entry
        ) doc_entries,
        LATERAL (
            SELECT doc_entries.entry->'resource' as resource
            WHERE (doc_entries.entry->'resource'->>'resourceType') = 'DocumentReference'
        ) doc_entry,
        LATERAL (
            SELECT jsonb_array_elements(doc_entry.resource->'content') as content
        ) contents
        WHERE content->'attachment'->>'data' IS NOT NULL
    """)
    notes_inserted = cursor.rowcount
    
    # Cleanup
    cursor.execute("TRUNCATE TABLE json_staging")
    conn.commit()
    
    return bundles_inserted, notes_inserted

def show_statistics(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM fhir_bundles")
    b_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM clinical_notes")
    n_count = cursor.fetchone()[0]
    print(f"\n📊 Totals: {b_count} Bundles | {n_count} Notes")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 load_synthea_sql_bulk.py <synthea_fhir_directory>")
        sys.exit(1)

    fhir_dir = sys.argv[1]
    if not os.path.exists(fhir_dir):
        print(f"❌ Directory not found: {fhir_dir}")
        sys.exit(1)

    conn = connect_db()
    try:
        create_tables_and_staging(conn)
        bulk_load_json_parallel(conn, fhir_dir)
        show_statistics(conn)
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    # Needed for Windows multiprocessing
    multiprocessing.freeze_support()
    main()

