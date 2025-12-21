# Quick Start: Generate Data with Clinical Notes

## 🚀 Fast Track (5 minutes)

```bash
# 1. Generate 100 test patients
cd scripts
./generate_synthea_data.sh 100

# 2. Start PostgreSQL (if not running)
docker-compose up -d postgres

# 3. Load data into database
python3 load_synthea_to_db.py ../synthea_output/fhir

# 4. Verify clinical notes
psql -h localhost -p 5433 -U postgres -d healthflow_fhir -c \
  "SELECT patient_id, LEFT(note_text, 100) FROM clinical_notes LIMIT 5;"
```

## 📊 Full Dataset (30-60 minutes)

```bash
# Generate 10,000 patients for production model
./generate_synthea_data.sh 10000
python3 load_synthea_to_db.py ../synthea_output/fhir
```

## ✅ Verify Setup

```bash
# Check Java version (need 11+)
java -version

# Check Python packages
pip install psycopg2-binary

# Test database connection
psql -h localhost -p 5433 -U postgres -d healthflow_fhir -c "SELECT 1;"
```

## 🎯 Next: BioBERT Integration

Once data is loaded:

1. Extract features with BioBERT (see `featurizer/` service)
2. Combine with structured features
3. Retrain XGBoost model
4. Compare: 77% → 82-85% accuracy

## 📝 Sample Output

```
🏥 HealthFlow-MS: Synthea Data Generation
==========================================

📋 Configuration:
   Patients to generate: 100
   Output directory: synthea_output

✅ Synthea already downloaded
🔬 Generating 100 synthetic patients...
   This may take several minutes...

✅ Data generation complete!

📊 Output structure:
   synthea_output/fhir/          - FHIR JSON bundles
   synthea_output/fhir/*.json    - Patient records with notes

📈 Generated 100 patient files

📝 Sample clinical note extraction:
   72yo M with history of CHF, DM2, HTN...
```
