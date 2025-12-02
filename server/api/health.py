from fastapi import APIRouter
from server.config.logger import get_logger
from server.config.settings import settings
from server.graph.graph import graph

router = APIRouter()
logger = get_logger("Health")

@router.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running and environment is configured correctly."""
    logger.info("Health check endpoint accessed")
    
    health_status = {
        "status": "healthy",
        "message": "API is running",
        "graph_initialized": graph is not None,
        "openai_api_key": "configured" if settings.openai_api_key else "not configured",
        "tavily_api_key": "configured" if settings.tavily_api_key else "not configured",
        "mongodb_uri": "configured" if settings.mongodb_uri else "not configured",
        "mongodb_db_name": "configured" if settings.mongodb_db_name else "not configured",
        "langchain_api_key": "configured" if settings.langchain_api_key else "not configured",
        "langchain_tracing_v2": "configured" if settings.langchain_tracing_v2 else "not configured",
    }
    
    # Return 200 even if graph is not initialized (app can still serve other endpoints)
    return health_status

