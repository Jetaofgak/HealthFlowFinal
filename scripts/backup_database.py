#!/usr/bin/env python3
"""
PostgreSQL Database Backup Script (Cross-platform)
Works on Mac, Linux, and Windows
"""

import subprocess
import os
from datetime import datetime
import sys

# Configuration
DB_NAME = "healthflow_fhir"
DB_USER = "postgres"
DB_PASSWORD = "qwerty"
CONTAINER_NAME = "postgres"  # Docker Compose service name
BACKUP_DIR = "database_backups"

def run_command(cmd, check=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check, 
            capture_output=True, 
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        sys.exit(1)

def main():
    print("📦 HealthFlow PostgreSQL Database Backup")
    print("=" * 50)
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename (no timestamp for simpler sharing)
    backup_file = os.path.join(BACKUP_DIR, "healthflow_db.sql")
    
    print(f"\n🔧 Configuration:")
    print(f"   Database: {DB_NAME}")
    print(f"   Container: {CONTAINER_NAME}")
    print(f"   Backup file: {backup_file}")
    print()
    
    # Find Docker container name
    print("🔍 Finding PostgreSQL container...")
    container_cmd = f"docker ps --filter name={CONTAINER_NAME} --format '{{{{.Names}}}}'"
    container_name = run_command(container_cmd).strip()
    
    if not container_name:
        print(f"❌ Error: PostgreSQL container '{CONTAINER_NAME}' not found")
        print("   Make sure Docker is running: docker-compose up -d")
        sys.exit(1)
    
    print(f"   Found: {container_name}")
    
    # Export database using Docker
    print("\n📤 Exporting database from Docker container...")
    dump_cmd = (
        f"docker exec {container_name} "
        f"pg_dump -U {DB_USER} -d {DB_NAME} "
        f"--clean --if-exists --create --format=plain"
    )
    
    # Set password environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    
    # Run pg_dump and save to file
    try:
        with open(backup_file, 'w') as f:
            subprocess.run(
                dump_cmd,
                shell=True,
                check=True,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e.stderr}")
        sys.exit(1)
    
    # Compress backup
    print("🗜️  Compressing backup...")
    import gzip
    import shutil
    
    backup_file_gz = f"{backup_file}.gz"
    with open(backup_file, 'rb') as f_in:
        with gzip.open(backup_file_gz, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Remove uncompressed file
    os.remove(backup_file)
    
    # Get file size
    file_size = os.path.getsize(backup_file_gz) / (1024 * 1024)  # MB
    
    print(f"\n✅ Backup complete!")
    print(f"   File: {backup_file_gz}")
    print(f"   Size: {file_size:.2f} MB")
    
    # Show database statistics
    print("\n📊 Database Statistics:")
    stats_cmd = f"""docker exec {container_name} psql -U {DB_USER} -d {DB_NAME} -c "
SELECT 
    'Patients' as table_name, COUNT(*) as records FROM raw_patients
UNION ALL
SELECT 'Encounters', COUNT(*) FROM raw_encounters
UNION ALL
SELECT 'Observations', COUNT(*) FROM raw_observations
UNION ALL
SELECT 'Conditions', COUNT(*) FROM raw_conditions
UNION ALL
SELECT 'Medications', COUNT(*) FROM raw_medications
UNION ALL
SELECT 'Readmissions', COUNT(*) FROM patient_readmissions
UNION ALL
SELECT 'FHIR Bundles', COUNT(*) FROM fhir_bundles;
" """
    
    print(run_command(stats_cmd))
    
    print("\n🎉 Ready to share!")
    print(f"\n💡 To restore on another machine:")
    print(f"   python restore_database.py {backup_file_gz}")

if __name__ == "__main__":
    main()
