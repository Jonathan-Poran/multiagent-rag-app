from fastapi import APIRouter
from server.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")

@router.get("")
async def welcome_message():
    logger.info("Welcome message endpoint accessed")
    
    welcome_message = """Welcome, I am a social influencer assistant agent.
    I can help you create content for your social media platforms.
    write for me the topic you want to create content."""

    return welcome_message