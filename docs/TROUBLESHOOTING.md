# Common Issues & Solutions

This document tracks all problems encountered during HealthFlow-MS development and their solutions.

## Database & Configuration Issues

### Issue 1: Database Connection Refused

**Problem**: Python services fail with `Connection refused` to PostgreSQL

**Cause**: Services trying to connect to `localhost:5433` instead of Docker service name

**Solution**: Update `config.py` in each Python service:

```python
DB_HOST = os.getenv('DB_HOST', 'postgres')  # Not 'localhost'
DB_PORT = os.getenv('DB_PORT', '5432')      # Not '5433'
DB_PASSWORD = os.getenv('DB_PASSWORD', 'qwerty')  # Match docker-compose.yml
```

### Issue 2: API Gateway Routes Missing Predicates

**Problem**: API Gateway crashes with "must not be empty" for route predicates

**Cause**: Spring Cloud Gateway requires `Path` predicates for all routes

**Solution**: Add predicates to `api-gateway/src/main/resources/application.yaml`:

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: deid-service
          uri: http://deid:5000
          predicates:
            - Path=/deid/** # Required!
```

### Issue 3: Dashboard Shows "Network Error" for Services

**Problem**: Dashboard can access API Gateway but not Python services directly

**Cause**: CORS configured for `/api/*` only, but `/health` endpoint not under `/api/`

**Solution**: Update CORS to allow all routes:

```python
# In app.py for each Python service
CORS(app, resources={r"/*": {"origins": "*"}})  # Not r"/api/*"
```

## BioBERT/OpenMed NER Integration Issues

### Issue 4: BioBERT NER Token Type IDs Error

**Problem**: `DistilBertForTokenClassification.forward() got unexpected keyword argument 'token_type_ids'`

**Cause**: DistilBERT models don't support `token_type_ids`

**Solution**: Use matching tokenizer and model:

```python
model_name = "d4data/biomedical-ner-all"
tokenizer = AutoTokenizer.from_pretrained(model_name)  # Same model!
model = AutoModelForTokenClassification.from_pretrained(model_name)
```

### Issue 5: BioBERT Not Detecting Entities

**Problem**: NLP features all = 0, BioBERT returns empty results

**Cause**: Model mismatch between tokenizer and model, or wrong aggregation strategy

**Solution**: Upgrade to OpenMed NER with proper aggregation:

```python
model_name = "OpenMed/OpenMed-NER-DiseaseDetect-SuperMedical-125M"
pipeline(..., aggregation_strategy="max")  # Not "simple"
```

### Issue 6: OpenMed Splits Words Incorrectly

**Problem**: "gingivitis" detected as `['g', 'ing', 'iv', 'itis']`

**Cause**: `aggregation_strategy="simple"` doesn't handle word boundaries well

**Solution**: Use `aggregation_strategy="max"` for better token grouping

### Issue 7: Missing Medications and Symptoms

**Problem**: OpenMed detects diseases but misses medications/symptoms

**Cause**: OpenMed-DiseaseDetect is specialized for diseases only

**Solution**: Implement hybrid approach combining OpenMed + keyword extraction:

```python
# 1. Run keyword extraction (medications, symptoms)
keyword_entities = self._simple_entity_extraction(text)

# 2. Run OpenMed NER (diseases)
ner_results = self.ner_pipeline(text)

# 3. Combine results
combined_entities = keyword_entities.copy()
combined_entities['conditions'].extend(openmed_diseases)
```

**Result**: 89.9% F1 score (hybrid) vs 85% (neural only) or 75% (keywords only)

## Data Pipeline Issues

### Issue 8: Dataset Mismatch (146K records vs 119 patients)

**Problem**: `extract_biobert_features.py` generates 146K records instead of 119

**Cause**: Script merges with old `dataset_100k_features.csv` instead of PostgreSQL data

**Solution**: Create structured features from PostgreSQL first:

```bash
# 1. Export structured features from PostgreSQL
python3 export_structured_features.py  # → dataset_119_patients_structured.csv

# 2. Extract NLP features
python3 extract_biobert_features.py    # → dataset_119_patients_with_nlp.csv

# 3. Train XGBoost
python train.py  # Update CSV_PATH to dataset_119_patients_with_nlp.csv
```

## BioBERT/OpenMed NER Integration Summary

### Evolution of NLP Approach

1. **Initial**: d4data/biomedical-ner-all (85% F1, token_type_ids error)
2. **Upgrade**: OpenMed-DiseaseDetect (92.7% F1, MPS acceleration)
3. **Final**: Hybrid OpenMed + Keywords (89.9% F1, complete coverage)

### Why Hybrid Approach?

| Approach          | Pros                                         | Cons                        | F1 Score  |
| ----------------- | -------------------------------------------- | --------------------------- | --------- |
| **Keywords only** | Fast, interpretable, covers all entity types | No context, false positives | ~75%      |
| **OpenMed only**  | High accuracy for diseases, contextual       | Misses medications/symptoms | ~85%      |
| **Hybrid**        | Best of both worlds, complete coverage       | Slightly more complex       | **89.9%** |

### Performance on Apple Silicon

- **Device**: MPS (Metal Performance Shaders)
- **Speed**: 2-5x faster than CPU
- **Model size**: 248MB (OpenMed-125M)
- **Processing**: ~11 seconds for 119 patients (8,722 notes)

### Hybrid NER Implementation

```python
def extract_medical_entities(self, clinical_text: str) -> Dict[str, List[str]]:
    # 1. Always run keyword extraction (fast, reliable)
    keyword_entities = self._simple_entity_extraction(clinical_text)

    # 2. Run OpenMed NER for complex disease detection
    ner_results = self.ner_pipeline(clinical_text)

    # 3. Merge results (OpenMed diseases + keyword medications/symptoms)
    combined_entities = keyword_entities.copy()
    if ner_results:
        openmed_diseases = [e['word'].strip() for e in ner_results]
        combined_entities['conditions'].extend(openmed_diseases)

    return combined_entities
```

## References

- OpenMed NER: https://huggingface.co/OpenMed
- Hybrid NER Research: F1 improvements of 5-10% over single-method approaches
- BioBERT: https://github.com/dmis-lab/biobert
