from fastapi import APIRouter
from src.dto import ChatRequest, ChatResponse
from src.services.graph_service import process_user_input
from src.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")


@router.post("", response_model=ChatResponse)
async def user_input(req: ChatRequest):
    """
    Handle user chat message in a conversation.
    
    Args:
        req: Chat request with message text and conversation_id.
    
    Returns:
        ChatResponse: Response with AI message text and conversation_id.
    """
    logger.info(f"Received chat message for conversation: {req.conversation_id}")
    try:
        result = await process_user_input(req.text, req.conversation_id)
        logger.info("Chat message processed successfully")
        
        # Convert result to ChatResponse
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise
