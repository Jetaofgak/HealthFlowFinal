from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (db connect) could go here
    # For now, we trust SQLAlchemy engine creation in services
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
