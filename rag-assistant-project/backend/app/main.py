from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.utils.logging_config import setup_logging, logger
from app.services.retrieval import RetrievalService
from app.services.generation import GenerationService
from app.api.routes.query import router as query_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Initializing application services at startup...")
    
    # Load retrieval service (ChromaDB vector store + embeddings) once at startup
    retrieval_service = RetrievalService()
    try:
        retrieval_service.initialize()
        app.state.retrieval_service = retrieval_service
    except Exception as e:
        logger.error(f"Failed to initialize retrieval service: {e}")
        app.state.retrieval_service = None

    # Load generation service once at startup
    generation_service = GenerationService()
    app.state.generation_service = generation_service

    logger.info("Application startup complete.")
    yield
    logger.info("Application shutting down...")

app = FastAPI(
    title="RAG Assistant API",
    version="1.0.0",
    description="FastAPI Backend for RAG Assistant Project",
    lifespan=lifespan
)

# Add CORS Middleware
origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(query_router)
