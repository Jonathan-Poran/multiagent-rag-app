from fastapi import APIRouter
from src.services.mongo_service import generate_conversation_id
from src.services.conversation_service import reset_conversation
from src.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")

@router.get("")
async def welcome_message():
    """
    Welcome message endpoint that generates a new conversation_id and resets the conversation state.
    
    Returns:
        dict: Welcome message and new conversation_id
    """
    logger.info("Welcome message endpoint accessed - generating new conversation")
    
    # Generate new conversation ID
    conversation_id = generate_conversation_id()
    
    # Reset the conversation state for this new ID
    reset_conversation(conversation_id)
    
    welcome_text = """Welcome, I am a social influencer assistant agent.
    I can help you create content for your social media platforms.
    write for me the topic you want to create content."""

    return {
        "message": welcome_text,
        "conversation_id": conversation_id
    }