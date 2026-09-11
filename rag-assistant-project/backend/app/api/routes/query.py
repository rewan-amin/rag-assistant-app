from fastapi import APIRouter, Request, HTTPException, status
from app.schemas.query import QueryRequest, QueryResponse
from app.core.config import settings
from app.utils.logging_config import logger

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/query", response_model=QueryResponse)
def handle_query(query_req: QueryRequest, request: Request):
    if not query_req.question or not query_req.question.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Question field cannot be empty."
        )

    retrieval_service = getattr(request.app.state, "retrieval_service", None)
    generation_service = getattr(request.app.state, "generation_service", None)

    if retrieval_service is None:
        try:
            logger.info("Attempting on-demand initialization of RetrievalService...")
            retrieval_service = RetrievalService()
            retrieval_service.initialize()
            request.app.state.retrieval_service = retrieval_service
        except Exception as e:
            logger.error(f"Failed on-demand retrieval service init: {e}")

    if generation_service is None:
        try:
            logger.info("Attempting on-demand initialization of GenerationService...")
            generation_service = GenerationService()
            request.app.state.generation_service = generation_service
        except Exception as e:
            logger.error(f"Failed on-demand generation service init: {e}")

    if retrieval_service is None or generation_service is None:
        logger.error("Services could not be initialized!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backend services are not initialized. Please ensure the ChromaDB vector store is populated and Ollama is running."
        )

    top_k = query_req.top_k if query_req.top_k is not None else settings.TOP_K

    try:
        context_chunks = retrieval_service.retrieve(
            question=query_req.question,
            top_k=top_k
        )
        answer, sources = generation_service.generate_answer(
            question=query_req.question,
            context_chunks=context_chunks
        )
        return QueryResponse(
            answer=answer,
            sources=sources,
            detections=None
        )
    except Exception as e:
        logger.error(f"Error handling query request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )
