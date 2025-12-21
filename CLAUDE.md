# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HealthFlow-MS is a microservices-based healthcare analytics platform that predicts patient readmission risks using FHIR (Fast Healthcare Interoperability Resources) standards. The system combines machine learning, NLP, and privacy-compliant data processing across seven specialized microservices.

## Commands

### Java Services (api-gateway, proxy-fhir)

```bash
# Build
cd api-gateway  # or proxy-fhir
./mvnw clean install

# Run
./mvnw spring-boot:run

# Test
./mvnw test
```

### Python Services (deID, featurizer, ml-predictor, score-api)

```bash
# Setup virtual environment (one-time)
cd deID  # or featurizer, ml-predictor, score-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run service
python app.py

# Run tests
pytest
```

### Frontend (dashboard-web)

```bash
cd dashboard-web

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Lint
npm run lint

# Preview production build
npm run preview
```

## System Architecture

### Microservices Pipeline

The system processes data through a sequential pipeline:

1. **ProxyFHIR** (Java/Spring Boot, port 8081) - Connects to FHIR servers and retrieves standardized medical resources (Patient, Observation, Condition, Medication, Procedure). Uses HAPI FHIR library to communicate with external FHIR servers.

2. **DeID** (Python/Flask, port 5000) - Anonymizes patient data using Faker library to replace identifiers with pseudonyms while preserving temporal patterns for analysis.

3. **Featurizer** (Python/Flask, port 5001) - Extracts clinical features from anonymized data. Processes both structured data (vital signs, lab results) and unstructured clinical notes using BioBERT for medical NLP.

4. **ModelRisque** (ml-predictor) (Python/Flask, port 5002) - Calculates 30-day readmission risk scores using XGBoost. Provides SHAP explanations for model interpretability.

5. **ScoreAPI** (Python/Flask, port 5003) - JWT-secured API for accessing patient risk scores. Provides authenticated endpoints for retrieving individual and batch predictions.

6. **API Gateway** (Java/Spring Cloud Gateway, port 8080) - Single entry point routing requests to microservices with CORS, logging, and rate limiting.

7. **Dashboard** (React/Vite) - Web interface for visualizing patient data, features, and risk predictions.

### Request Routing

The API Gateway routes requests based on URL paths:
- `/api/v1/fhir/**` → ProxyFHIR (port 8081)
- `/api/v1/deid/**` → DeID (port 5000)
- `/api/v1/features/**` → Featurizer (port 5001)
- `/api/v1/predictions/**` → ML Predictor (port 5002)
- `/api/v1/scores/**` → ScoreAPI (port 5003)

### Data Flow

```
FHIR Server → ProxyFHIR → PostgreSQL → DeID → PostgreSQL →
Featurizer → PostgreSQL → ML Predictor → PostgreSQL → Dashboard
```

All Python services share a PostgreSQL database (default port 5433, db name: `healthflow_fhir`) for storing FHIR bundles, anonymized data, extracted features, and predictions.

## Key Technical Patterns

### Python Services Structure

All Python services follow a consistent Flask blueprint architecture:

```
service/
├── app.py              # Flask app factory with create_app()
├── config.py           # Environment-based configuration (DevelopmentConfig, ProductionConfig)
├── routes/             # Blueprint definitions for REST endpoints
├── models/             # SQLAlchemy ORM models
├── database/           # Database connection management
├── [core_logic]/       # Service-specific logic (anonymizer/, extractors/, calculators/)
├── tests/              # pytest test files
├── requirements.txt    # Python dependencies
└── .env               # Environment variables (DB credentials, ports)
```

### Configuration Management

**Python services**: Use `python-dotenv` to load `.env` files. Configuration classes in `config.py` support multiple environments. Database connection pooling is configured via `SQLALCHEMY_ENGINE_OPTIONS`.

**Java services**: Use Spring Boot's `application.yaml` for configuration. Database credentials and service URLs are externalized. HAPI FHIR server URL configured in `hapi.fhir.server-url`.

### Database Schema

Key tables:
- FHIR bundles (stored by ProxyFHIR)
- Anonymized patient records (stored by DeID)
- Extracted features (stored by Featurizer)
- Risk predictions with SHAP values (stored by ML Predictor)

### Feature Engineering

The Featurizer service extracts features through specialized modules:
- `patient_features.py` - Demographics, age bins
- `vital_signs_features.py` - Blood pressure, heart rate, BMI categories
- `lab_results_features.py` - Lab test results, outlier detection

Feature configuration (age bins, BMI categories, BP thresholds) is defined in `featurizer/config.py`.

### ML Model

The XGBoost model (`xgboost_readmission_model.ubj` at project root) is loaded by the ml-predictor service. SHAP library provides local explanations for each prediction. Model training scripts (`train_freeze.py`) are available at the root level.

## Development Notes

### Running the Full Stack

1. Start PostgreSQL database (port 5433)
2. Start Java services: api-gateway (8080), proxy-fhir (8081)
3. Start Python services: deID (5000), featurizer (5001), ml-predictor (5002)
4. Start frontend: dashboard-web (Vite dev server)

All services must be running for the complete pipeline to work.

### Database Requirements

All Python services expect PostgreSQL connection on `localhost:5433` with database `healthflow_fhir`. Credentials configured in each service's `.env` file.

### FHIR Server Connection

ProxyFHIR connects to SMART Health IT test server by default (`https://r4.smarthealthit.org`). This is configured in `proxy-fhir/src/main/resources/application.yaml`.

### Privacy Compliance

DeID service implements GDPR/HIPAA compliance by removing direct identifiers before any analytics processing. Never bypass the DeID step in the pipeline.

### Model Explainability

ML predictions must include SHAP values for clinical decision support. The ml-predictor service generates both risk scores (0-1 probability) and feature importance explanations.
