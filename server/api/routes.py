from fastapi import FastAPI, APIRouter
from . import get_graph_png, user_input, welcome_message, user_input_food
from server.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")


def register_routes(app: FastAPI):
    """Register all API routes with the FastAPI application."""
    logger.info("Registering API routes")
    # Register health check endpoint
    app.include_router(router)
    app.include_router(welcome_message.router, prefix="/welcome-message", tags=["Welcome Message"])
    app.include_router(get_graph_png.router, prefix="/get-graph-png", tags=["Get Graph Png"])
    app.include_router(user_input.router, prefix="/user-input", tags=["User Input"])
    app.include_router(user_input_food.router, prefix="/user-input-food", tags=["User Input Food"])
    logger.info("All API routes registered successfully")


@router.get("/")
def root():
    return {"status": "ok"}

@router.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    from server.graph.graph import graph
    from server.config.settings import settings
    
    health_status = {
        "status": "healthy",
        "message": "API is running",
        "graph_initialized": graph is not None,
        "openai_configured": bool(settings.openai_api_key)
    }
    
    # Return 200 even if graph is not initialized (app can still serve other endpoints)
    return health_status
