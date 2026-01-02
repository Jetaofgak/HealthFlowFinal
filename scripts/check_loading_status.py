import psycopg2
import time

# Database configuration (same as loader)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'healthflow_fhir',
    'user': 'postgres',
    'password': 'qwerty'
}

def check_status():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. Check Staging Table (should be full)
        cursor.execute("SELECT count(*) FROM json_staging;")
        staging_count = cursor.fetchone()[0]
        print(f"📦 Rows in staging (json_staging): {staging_count}")
        
        # 2. Check Destination Tables (might be 0 until commit)
        cursor.execute("SELECT count(*) FROM fhir_bundles;")
        bundles_count = cursor.fetchone()[0]
        
        # Check Table Sizes (Best indicator of writing)
        cursor.execute("SELECT pg_size_pretty(pg_total_relation_size('fhir_bundles')), pg_size_pretty(pg_total_relation_size('clinical_notes'));")
        sizes = cursor.fetchone()
        
        print(f"✅ Committed Bundles: {bundles_count}")
        print(f"📊 Table Sizes: Bundles={sizes[0]} | Notes={sizes[1]} (Run this script again to see it grow)")
        
        # 3. Check Active Queries
        print("\n⚙️  Active Database Queries:")
        cursor.execute("""
            SELECT pid, state, now() - query_start as duration, query 
            FROM pg_stat_activity 
            WHERE state = 'active' 
            AND query NOT LIKE '%pg_stat_activity%'
            AND datname = 'healthflow_fhir';
        """)
        
        queries = cursor.fetchall()
        if not queries:
            print("   No active queries found.")
        else:
            for q in queries:
                print(f"   [{q[2]}] {q[3][:100]}...")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_status()
