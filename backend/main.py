"""
FastAPI Application Entry Point for TRACENET Backend.
Configures CORS, mounts API routes, and manages application lifecycle.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the project root is on sys.path so that ingestion/, graph/, ai/, scoring/, reports/ are importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.services.state import app_state
from backend.routes.upload import router as upload_router
from backend.routes.search import router as search_router
from backend.routes.analysis import router as analysis_router
from backend.routes.export import router as export_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: pre-load the SentenceTransformer model so first request is fast."""
    print("[TRACENET] Loading AI Stylometry Model...")
    app_state.initialize_model()
    print(f"[TRACENET] Model loaded: {app_state.stylometer.embedding_engine.engine_type}")
    yield
    # Shutdown cleanup
    if app_state.graph and app_state.graph.neo4j_client:
        app_state.graph.neo4j_client.close()
    print("[TRACENET] Shutdown complete.")


app = FastAPI(
    title="TRACENET API",
    description="Threat Actor Intelligence & Attribution Platform — REST API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allow frontend dev server and production deployments
frontend_url = os.getenv("FRONTEND_URL")
allowed_origins = [frontend_url] if frontend_url else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount route modules
app.include_router(upload_router, prefix="/api", tags=["Upload & Processing"])
app.include_router(search_router, prefix="/api", tags=["Search & Profiles"])
app.include_router(analysis_router, prefix="/api", tags=["Analysis & Evidence"])
app.include_router(export_router, prefix="/api", tags=["Export"])


@app.get("/api/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "online",
        "system": "TRACENET",
        "data_loaded": app_state.is_processed,
        "model": app_state.stylometer.embedding_engine.engine_type if app_state.stylometer else "Not loaded",
        "neo4j": app_state.graph.neo4j_active if app_state.graph else False
    }
