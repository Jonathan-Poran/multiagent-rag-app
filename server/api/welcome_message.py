from fastapi import APIRouter
from server.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")

@router.get("")
async def welcome_message():
    logger.info("Welcome message endpoint accessed")
    return "Welcome to the multi-agent RAG application!"