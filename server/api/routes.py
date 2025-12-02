from fastapi import FastAPI, APIRouter
from . import get_graph_png, user_input, welcome_message, user_input_food, health
from server.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")


def register_routes(app: FastAPI):
    """Register all API routes with the FastAPI application."""
    logger.info("Registering API routes")
    
    # Register root endpoint
    app.include_router(router)
    
    # Register health check endpoint
    app.include_router(health.router, tags=["Health"])
    
    # Register other endpoints
    app.include_router(welcome_message.router, prefix="/welcome-message", tags=["Welcome Message"])
    app.include_router(get_graph_png.router, prefix="/get-graph-png", tags=["Get Graph Png"])
    app.include_router(user_input.router, prefix="/user-input", tags=["User Input"])
    app.include_router(user_input_food.router, prefix="/user-input-food", tags=["User Input Food"])
    logger.info("All API routes registered successfully")


@router.get("/")
def root():
    return {"status": "ok"}
