from fastapi import APIRouter
from pydantic import BaseModel
from server.services.multiagent import process_user_input
from server.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")


class ChatRequest(BaseModel):
    text: str
    conversation_id: str


@router.post("")
async def user_input(req: ChatRequest):
    """
    Handle user chat message in a conversation.
    
    Args:
        req: Chat request with message text and conversation_id.
    
    Returns:
        dict: Response with AI message text.
    """
    logger.info(f"Received chat message for conversation: {req.conversation_id}")
    try:
        result = await process_user_input(req.text, req.conversation_id)
        logger.info("Chat message processed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise
