from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.config import get_settings
from app.schemas import AgentRequest, IngestRequest, SearchRequest
from app.services.agent import run_agent
from app.services.ingestion import ingest_directory
from app.services.qdrant_store import QdrantStore


@asynccontextmanager
async def lifespan(_: FastAPI):
    QdrantStore().ensure_collection()
    yield


app = FastAPI(
    title=get_settings().app_name,
    version="1.0.0",
    description="A fresher-friendly learning project for RAG, AI agents, APIs, and automation.",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": get_settings().app_name}


@app.post("/api/ingest")
def ingest(request: IngestRequest) -> dict:
    try:
        return ingest_directory(request.directory)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/search")
def search_documents(request: SearchRequest) -> dict:
    try:
        results = QdrantStore().search(request.query, request.top_k)
        return {"query": request.query, "results": [item.__dict__ for item in results]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/agent")
def agent(request: AgentRequest) -> dict:
    try:
        return run_agent(request.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
