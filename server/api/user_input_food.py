# server/api/user_input_food.py

from fastapi import APIRouter
from pydantic import BaseModel
from server.services.multiagent import process_user_input_food
from server.config.logger import get_logger

router = APIRouter()
logger = get_logger("FastAPI_Server")

class FoodRequest(BaseModel):
    text: str

@router.post("")
async def user_input_food(req: FoodRequest):
    logger.info(f"Received user input food request")
    try:
        result = await process_user_input_food(req.text)
        logger.info("User input food request processed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing user input food: {e}", exc_info=True)
        raise
