from fastapi import APIRouter, HTTPException
from server.graph.graph import graph

router = APIRouter()

@router.get("")
async def get_graph():
    return "graph.png"