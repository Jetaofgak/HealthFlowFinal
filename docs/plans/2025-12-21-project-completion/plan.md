# Project Completion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: use executing-plans skill to implement this plan task-by-task.

**Goal:** Complete the HealthFlow-MS platform by migrating ScoreAPI to FastAPI and implementing the missing AuditFairness service, achieving full compliancy with project specifications.

**Architecture:** Microservices architecture using Docker Compose. ScoreAPI (FastAPI) orchestrates predictions. AuditFairness (EvidentlyAI + Dash) monitors model drift decoupled from the main path.

**Tech Stack:** Python 3.9+, FastAPI, Uvicorn, Flask (being replaced), EvidentlyAI, Dash, PostgreSQL, Docker.

---

### Task 1: Migrate ScoreAPI Structure

**Files:**

- Create: `score-api/requirements.txt`
- Modify: `score-api/Dockerfile`

**Step 1: Update Dependencies**
Replace Flask dependencies with FastAPI requirements.

```text
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
pytest==7.4.3
httpx==0.26.0
```

**Step 2: Update Dockerfile**
Switch to Uvicorn command.

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port (5003 matched in docker-compose)
EXPOSE 5003

# Run with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5003", "--reload"]
```

**Step 3: Verify Dependencies**
Build the image to check for conflicts (dry run).

```bash
docker build -t test-score-api ./score-api
```

Expected: Successfully built image.

---

### Task 2: Implement ScoreAPI Main Application

**Files:**

- Create: `score-api/app.py`
- Create: `score-api/config.py`

**Step 1: Create FastAPI Entry Point**
Setup basic app with CORS and DB connection.

```python
# score-api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (db connect) could go here
    yield
    # Shutdown logic

app = FastAPI(title="HealthFlow Score API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "score-api"}

# Import routes later: app.include_router(...)
```

**Step 2: Create Settings**
Use Pydantic for strict config.

```python
# score-api/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str
    PORT: int = 5003
    ML_PREDICTOR_URL: str
    JWT_SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
```

**Step 3: Verify App Boots**
Check syntax.

```bash
python3 -m py_compile score-api/app.py
```

Expected: No output (success).

---

### Task 3: Implement AuditFairness Service

**Files:**

- Create: `audit-fairness/requirements.txt`
- Create: `audit-fairness/Dockerfile`
- Create: `audit-fairness/app.py`
- Create: `audit-fairness/monitor.py`

**Step 1: Setup Dependencies**

```text
evidently==0.4.16
dash==2.14.2
pandas==2.1.4
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
```

**Step 2: Setup Dockerfile**
Reflect port 5004.

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5004
CMD ["python", "app.py"]
```

**Step 3: Basic Dash App**
Scaffold the dashboard.

```python
# audit-fairness/app.py
import dash
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("HealthFlow AI Fairness Audit"),
    html.Div("EvidentlyAI Reports will appear here.")
])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
```

**Step 4: Verify**
Syntax check.

```bash
python3 -m py_compile audit-fairness/app.py
```

---

### Task 4: Integration & Update Docker Compose

**Files:**

- Modify: `docker-compose.yml`

**Step 1: Update Composition**
Add the new service and update ScoreAPI command if needed (already handled in Dockerfile).

```yaml
# ... existing services ...

# AuditFairness Service
audit-fairness:
  build:
    context: ./audit-fairness
    dockerfile: Dockerfile
  container_name: healthflow-audit-fairness
  ports:
    - "5004:5004"
  environment:
    SQLALCHEMY_DATABASE_URI: postgresql://postgres:qwerty@postgres:5432/healthflow_fhir
    PORT: 5004
  depends_on:
    postgres:
      condition: service_healthy
# ...
```

**Step 2: Verify Config**

```bash
docker-compose config
```

Expected: Valid YAML output with tracking of new service.
