from fastapi import APIRouter
from src.config.logger import get_logger
from src.config.settings import settings

router = APIRouter()
logger = get_logger("Health")


@router.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running and environment is configured correctly."""
    logger.info("Health check endpoint accessed")
    
    return {"status": "OK"}

