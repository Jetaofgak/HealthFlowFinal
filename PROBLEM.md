# Dashboard Data Display Issue - Solved

## Problem Description

The dashboard at `http://localhost:3000/` was displaying **zeros and N/A values** despite having 3,607 patients in the database with trained ML model predictions.

### Symptoms

```
Dashboard showing:
- Total Patients: 0
- Average Age: N/A
- High Risk: 0
- Predictions: 0
- All charts empty
```

API responses returning empty data:
```bash
curl http://localhost:8085/api/v1/features/stats
# {"total_patients": 0, "average_age": null, "average_bmi": null, "average_cholesterol": null}

curl http://localhost:8085/api/v1/predictions/stats
# {"total_predictions": 0, "risk_distribution": {}, ...}
```

### Additional Error

After fixing the data issue, dashboard displayed briefly then went **black** with console error:
```
TypeError: featureStats.average_age.toFixed is not a function
```

---

## Root Cause Analysis

### Issue 1: Two Separate Data Pipelines

The project has **TWO INDEPENDENT data pipelines** that were not connected:

#### Pipeline 1: Training Workflow (SQL-Based) ✅ Working
```
Synthea Data
  → load_synthea_to_db.py
  → raw_* tables (raw_patients, raw_observations, raw_conditions)
  → build_dataset_pure_sql.sql
  → dataset_final (3,607 patients with features)
  → extract_biobert_features.py
  → dataset_with_nlp.csv
  → train.py
  → xgboost_readmission_model.ubj (81% accuracy)
```

**Purpose**: Generate training data and build ML model
**Tables populated**: `dataset_final`, `raw_*` tables
**Status**: ✅ Complete and working

#### Pipeline 2: Microservices API Workflow ❌ Empty
```
fhir_resources (4.7M FHIR records)
  → DeID Service (/api/v1/deid/anonymize/all)
  → fhir_resources_anonymized (0 rows ❌)
  → Featurizer Service (/api/v1/features/extract/all)
  → patient_features (0 rows ❌)
  → ML-Predictor Service (/api/v1/predictions/predict/all)
  → risk_predictions (0 rows ❌)
  → Dashboard API calls
  → Returns zeros/N/A ❌
```

**Purpose**: Serve data to dashboard via REST APIs
**Tables needed**: `patient_features`, `risk_predictions`
**Status**: ❌ Empty tables - dashboard queries returned no data

### Issue 2: Type Mismatch in Dashboard

PostgreSQL returns `NUMERIC` types as strings in JSON:
```json
{"average_age": "45.8"}  // String, not number!
```

React Dashboard code expected numbers:
```javascript
featureStats.average_age.toFixed(1)  // ❌ Crashes - strings don't have toFixed()
```

---

## Solution Implemented

### Fix 1: Bridge the Two Pipelines

Created SQL script to populate microservice tables from the existing training dataset:

**File**: `scripts/populate_microservice_tables.sql`

```sql
-- Populate patient_features from dataset_final
INSERT INTO patient_features (patient_id, age, gender, bmi, ...)
SELECT patient_id, age,
       CASE WHEN gender_male = 1 THEN 'male' ELSE 'female' END,
       vit_bmi, ...
FROM dataset_final;

-- This populated 3,607 patient feature records
```

Then triggered the ML-Predictor service to generate real predictions:
```bash
curl -X POST http://localhost:8085/api/v1/predictions/predict/all
# Generated 3,607 predictions using the trained XGBoost model
```

**Result**:
- `patient_features`: 3,607 rows ✅
- `risk_predictions`: 3,607 rows ✅
- Dashboard APIs now return real data ✅

### Fix 2: Parse String Numbers in Dashboard

Modified Dashboard.jsx to parse numeric strings before formatting:

**File**: `dashboard-web/src/components/Dashboard.jsx`

```javascript
// Before (crashed):
featureStats.average_age.toFixed(1)

// After (works):
parseFloat(featureStats.average_age).toFixed(1)
```

Applied to all numeric fields:
- `average_age`
- `average_bmi`
- `average_cholesterol`
- `average_framingham_score`

---

## Database State Analysis

### Before Fix
```sql
SELECT 'dataset_final (Training)', COUNT(*) FROM dataset_final;
-- 3,607 rows ✅

SELECT 'patient_features (Microservice)', COUNT(*) FROM patient_features;
-- 0 rows ❌

SELECT 'risk_predictions (Microservice)', COUNT(*) FROM risk_predictions;
-- 0 rows ❌
```

### After Fix
```sql
SELECT 'patient_features', COUNT(*) FROM patient_features;
-- 3,607 rows ✅

SELECT 'risk_predictions', COUNT(*) FROM risk_predictions;
-- 3,607 rows ✅

-- Risk distribution
SELECT risk_category, COUNT(*) FROM risk_predictions GROUP BY risk_category;
-- high     | 1,559 (43%)
-- moderate | 1,441 (40%)
-- low      |   607 (17%)
```

---

## Why This Happened

### Design Issue

The README documented the **training workflow** clearly but didn't document how to populate the **microservice tables** that the dashboard depends on.

The training workflow creates `dataset_final` for model training, but the dashboard queries `patient_features` and `risk_predictions` tables via microservice APIs.

### DeID Service Limitation

Attempting to use the DeID service to populate data from scratch failed:
```bash
curl -X POST http://localhost:8085/api/v1/deid/anonymize/all
# Tried to process 4.7M FHIR resources (1.8M observations)
# Service crashed with exit code 247 (out of memory)
```

The microservice approach works for small datasets but not for the full 4.7M FHIR resources.

---

## Best Practice Solution

For projects with existing trained models and datasets, use the **SQL-based bridge approach**:

1. **Training**: Use SQL workflow → `dataset_final` → train model ✅
2. **Dashboard**: Populate microservice tables from `dataset_final` ✅
3. **Predictions**: Use ML-Predictor service for real-time inference ✅

This approach:
- ✅ Reuses existing data (no need to reprocess 4.7M records)
- ✅ Fast (SQL is instant vs. microservice processing)
- ✅ Uses real ML model predictions (not heuristics)
- ✅ Avoids memory issues from processing millions of records

---

## Files Changed

### New Files
1. `scripts/populate_microservice_tables.sql` - Populates patient_features and risk_predictions from dataset_final

### Modified Files
1. `dashboard-web/src/components/Dashboard.jsx` - Added parseFloat() for numeric string handling
2. `README.md` - Added microservice table population step

### Commits
```
b61259c7 fix: parse API numeric values as floats before calling toFixed
e2181ada fix: populate microservice tables from dataset_final for dashboard
```

---

## Verification Steps

### 1. Check Database Tables
```bash
export PGPASSWORD='qwerty'
psql -h localhost -p 5433 -U postgres -d healthflow_fhir -c "
  SELECT 'patient_features', COUNT(*) FROM patient_features
  UNION ALL
  SELECT 'risk_predictions', COUNT(*) FROM risk_predictions;
"
# Should show 3,607 rows for each
```

### 2. Test API Endpoints
```bash
curl http://localhost:8085/api/v1/features/stats
# Should return: {"total_patients": 3607, "average_age": "45.8", ...}

curl http://localhost:8085/api/v1/predictions/stats
# Should return: {"total_predictions": 3607, "risk_distribution": {...}, ...}
```

### 3. Check Dashboard
```bash
open http://localhost:3000/
# Should display:
# - Total Patients: 3,607
# - Average Age: 45.8 yrs
# - High Risk: 1,559
# - Predictions: 3,607
# - Charts populated with risk distribution
```

---

## Lessons Learned

1. **Document both pipelines**: Training workflow ≠ Production workflow
2. **Type safety**: PostgreSQL NUMERIC → JSON string, not number
3. **Scalability**: Microservices can't process millions of records in-memory
4. **Bridge patterns**: SQL-based data migration is faster than re-processing

---

## Future Improvements

### Option 1: Batch Processing for DeID Service
Modify DeID service to process data in batches:
```python
# Process 1,000 patients at a time instead of all 3,607
for batch in chunks(patients, batch_size=1000):
    anonymize_batch(batch)
    session.commit()  # Commit after each batch
```

### Option 2: Direct Database Population
Skip the microservice layer entirely for bulk operations:
```sql
-- Directly insert into patient_features from raw_* tables
-- Much faster than calling APIs 3,607 times
```

### Option 3: API Response Type Fixing
Modify Python Flask routes to return numbers, not strings:
```python
# In featurizer/routes/feature_routes.py
return jsonify({
    'average_age': float(avg_age) if avg_age else None,  # Force float
    'average_bmi': float(avg_bmi) if avg_bmi else None,
})
```

---

## Related Issues

- Dashboard showing zeros: #dashboard-zero-data ✅ Fixed
- Black screen error: #dashboard-tofixed-error ✅ Fixed
- DeID service crash: #deid-oom (Not blocking - workaround implemented)
