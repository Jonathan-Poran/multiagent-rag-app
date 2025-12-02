from fastapi import APIRouter
from server.services.conversation import reset_conversation
from server.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")

@router.get("")
async def welcome_message():
    """
    Welcome message endpoint that resets the conversation state.
    """
    logger.info("Welcome message endpoint accessed - resetting conversation")
    
    # Reset the conversation
    reset_conversation()
    
    welcome_message = """Welcome, I am a social influencer assistant agent.
    I can help you create content for your social media platforms.
    write for me the topic you want to create content."""

    return welcome_message