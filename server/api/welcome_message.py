from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def welcome_message():
    return "Welcome to the multi-agent RAG application!"