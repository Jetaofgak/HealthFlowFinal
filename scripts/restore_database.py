#!/usr/bin/env python3
"""
PostgreSQL Database Restore Script (Cross-platform)
Works on Mac, Linux, and Windows
"""

import subprocess
import os
import sys
import gzip
import shutil

# Configuration
DB_NAME = "healthflow_fhir"
DB_USER = "postgres"
DB_PASSWORD = "qwerty"
CONTAINER_NAME = "postgres"  # Docker Compose service name

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
    print("📥 HealthFlow PostgreSQL Database Restore")
    print("=" * 50)
    
    # Check if backup file provided
    if len(sys.argv) < 2:
        print("❌ Error: No backup file specified")
        print("\nUsage: python restore_database.py <backup_file.sql.gz>")
        print("Example: python restore_database.py database_backups/healthflow_db_20251221_150000.sql.gz")
        sys.exit(1)
    
    backup_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(backup_file):
        print(f"❌ Error: Backup file not found: {backup_file}")
        sys.exit(1)
    
    print(f"\n🔧 Configuration:")
    print(f"   Backup file: {backup_file}")
    print(f"   Database: {DB_NAME}")
    print(f"   Container: {CONTAINER_NAME}")
    print()
    
    # Find Docker container
    print("🔍 Finding PostgreSQL container...")
    container_cmd = f"docker ps --filter name={CONTAINER_NAME} --format '{{{{.Names}}}}'"
    container_name = run_command(container_cmd).strip()
    
    if not container_name:
        print(f"❌ Error: PostgreSQL container '{CONTAINER_NAME}' not found")
        print("   Make sure Docker is running: docker-compose up -d")
        sys.exit(1)
    
    print(f"   Found: {container_name}")
    
    # Decompress if needed
    sql_file = backup_file
    if backup_file.endswith('.gz'):
        print("\n🗜️  Decompressing backup...")
        sql_file = backup_file[:-3]  # Remove .gz extension
        with gzip.open(backup_file, 'rb') as f_in:
            with open(sql_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    # Restore database
    print("\n📥 Restoring database...")
    print("   This may take a few minutes...")
    
    # Copy SQL file to container
    copy_cmd = f"docker cp {sql_file} {container_name}:/tmp/restore.sql"
    run_command(copy_cmd)
    
    # Restore from SQL file
    restore_cmd = (
        f"docker exec {container_name} "
        f"psql -U {DB_USER} -f /tmp/restore.sql"
    )
    
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    
    try:
        subprocess.run(
            restore_cmd,
            shell=True,
            check=True,
            env=env,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Restore failed: {e.stderr}")
        sys.exit(1)
    
    # Cleanup
    cleanup_cmd = f"docker exec {container_name} rm /tmp/restore.sql"
    run_command(cleanup_cmd, check=False)
    
    if backup_file.endswith('.gz') and os.path.exists(sql_file):
        os.remove(sql_file)
    
    print("\n✅ Restore complete!")
    
    # Verify restoration
    print("\n📊 Verifying database:")
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
    
    print("\n🎉 Database ready to use!")
    print("\n💡 Next steps:")
    print("   1. Verify data: docker exec -it <container> psql -U postgres -d healthflow_fhir")
    print("   2. Run feature extraction: cd scripts && python3 extract_biobert_features.py")
    print("   3. Train model: python train.py")

if __name__ == "__main__":
    main()
