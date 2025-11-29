from fastapi import FastAPI, APIRouter
from . import get_graph_png, user_input, welcome_message, user_input_food

router = APIRouter()


def register_routes(app: FastAPI):
    """Register all API routes with the FastAPI application."""
    app.include_router(welcome_message.router, prefix="/welcome-message", tags=["Welcome Message"])
    app.include_router(get_graph_png.router, prefix="/get-graph-png", tags=["Get Graph Png"])
    app.include_router(user_input.router, prefix="/user-input", tags=["User Input"])
    app.include_router(user_input_food.router, prefix="/user-input-food", tags=["User Input Food"])




@router.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {
        "status": "healthy",
        "message": "API is running"
    }
