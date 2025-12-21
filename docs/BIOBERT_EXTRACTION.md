# BioBERT Feature Extraction Guide

## Overview

This script extracts NLP features from clinical notes using BioBERT and combines them with structured features to create an enhanced dataset for XGBoost training.

## Prerequisites

```bash
# 1. Ensure PostgreSQL is running with clinical notes
docker-compose ps postgres

# 2. Verify clinical notes exist
psql -h localhost -p 5433 -U postgres -d healthflow_fhir -c \
  "SELECT COUNT(*) FROM clinical_notes;"

# 3. Install dependencies (if running outside Docker)
cd featurizer
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Usage

### Quick Start

```bash
cd scripts
python3 extract_biobert_features.py
```

### Expected Output

```
🏥 BioBERT Feature Extraction Pipeline
==================================================
Initializing BioBERT service...
BioBERT service loaded successfully
Connecting to PostgreSQL...
Loading clinical notes from database...
Loaded 8722 clinical notes for 119 patients
Loading structured features from dataset_100k_features.csv...
Loaded 100000 records with 35 features
Extracting NLP features from clinical notes...
Processing patients: 100%|████████████| 119/119 [02:15<00:00]
Extracted NLP features for 119 patients
Combining structured and NLP features...
Combined dataset: 100000 records, 49 features
Saving enhanced dataset to dataset_with_nlp_features.csv...

📊 Dataset Statistics:
   Total records: 100000
   Structured features: 35
   NLP features: 14
   Total features: 49

📝 Sample NLP Features (first patient):
   nlp_num_conditions: 5
   nlp_has_chf: 1
   nlp_has_copd: 0
   nlp_has_diabetes: 1
   nlp_has_hypertension: 1

🎉 Feature extraction complete!
✅ Enhanced dataset saved to: dataset_with_nlp_features.csv

💡 Next step: Retrain XGBoost model with:
   python train.py  # Update CSV_PATH to 'dataset_with_nlp_features.csv'
```

## NLP Features Extracted

The script extracts 14 NLP-derived features:

### Comorbidity Features

- `nlp_num_conditions`: Total number of conditions mentioned
- `nlp_has_chf`: Has congestive heart failure (0/1)
- `nlp_has_copd`: Has COPD (0/1)
- `nlp_has_ckd`: Has chronic kidney disease (0/1)
- `nlp_has_diabetes`: Has diabetes (0/1)
- `nlp_has_hypertension`: Has hypertension (0/1)

### Medication Features

- `nlp_num_medications`: Number of medications mentioned
- `nlp_polypharmacy`: Taking 5+ medications (0/1)

### Complexity Indicators

- `nlp_note_length`: Total characters in all notes
- `nlp_note_count`: Number of clinical notes
- `nlp_avg_note_length`: Average note length

### Symptom Features

- `nlp_num_symptoms`: Number of symptoms mentioned
- `nlp_has_pain`: Has pain symptoms (0/1)
- `nlp_has_dyspnea`: Has breathing difficulties (0/1)

## Data Flow

```
PostgreSQL (clinical_notes)
         ↓
   BioBERT NER
         ↓
   Extract Entities
         ↓
   Generate Features (14 NLP features)
         ↓
   Merge with Structured Features (35 features)
         ↓
   Enhanced Dataset (49 features)
         ↓
   dataset_with_nlp_features.csv
```

## Performance Impact

Expected improvements after retraining:

| Metric        | Before (Structured Only) | After (+ NLP Features) |
| ------------- | ------------------------ | ---------------------- |
| **Accuracy**  | 77.28%                   | 82-85%                 |
| **ROC-AUC**   | 87.36%                   | 90-93%                 |
| **Precision** | 66%                      | 72-76%                 |
| **Recall**    | 76%                      | 80-84%                 |

## Troubleshooting

### BioBERT Model Not Loading

```bash
# Download BioBERT model manually
cd featurizer
python -c "from services.biobert_service import BioBERTService; BioBERTService()"
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Verify connection
psql -h localhost -p 5433 -U postgres -d healthflow_fhir -c "SELECT 1;"
```

### Out of Memory

```bash
# Process in smaller batches (modify script)
# Or increase Docker memory limit
```

## Next Steps

After feature extraction:

1. **Verify Output**:

   ```bash
   head -5 ../dataset_with_nlp_features.csv
   wc -l ../dataset_with_nlp_features.csv
   ```

2. **Update train.py**:

   ```python
   # Line 16
   CSV_PATH = "dataset_with_nlp_features.csv"
   ```

3. **Retrain Model**:

   ```bash
   cd ..
   python train.py
   ```

4. **Compare Results**:
   - Check accuracy improvement
   - Analyze feature importance
   - Update model file

## Advanced Usage

### Extract for Specific Patients

Modify the script to filter patients:

```python
# In load_clinical_notes()
query = """
SELECT patient_id, note_text
FROM clinical_notes
WHERE patient_id IN ('patient1', 'patient2')
ORDER BY patient_id, note_date
"""
```

### Custom Feature Engineering

Add custom NLP features in `ClinicalNLPExtractor.extract_features_from_notes()`:

```python
features = {
    # ... existing features ...
    'nlp_has_cancer': int(self._has_condition(entities, ['cancer', 'malignancy'])),
    'nlp_has_sepsis': int(self._has_condition(entities, ['sepsis', 'septic'])),
}
```

## Time Estimates

- **100 patients**: ~2-3 minutes
- **1,000 patients**: ~15-20 minutes
- **10,000 patients**: ~2-3 hours
- **100,000 patients**: ~20-30 hours

Processing time depends on:

- Number of clinical notes per patient
- Average note length
- CPU/GPU availability
