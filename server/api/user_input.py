from fastapi import APIRouter
from server.services.multiagent import process_user_input_food

router = APIRouter()

@router.post("")
async def user_input(text: str):
    return "process_user_input(text)"