# server/api/user_input_food.py

from fastapi import APIRouter
from pydantic import BaseModel
from server.services.multiagent import process_user_input_food

router = APIRouter()

class FoodRequest(BaseModel):
    text: str

@router.post("")
async def user_input_food(req: FoodRequest):
    return await process_user_input_food(req.text)
