import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from src.config.logger import get_logger
from src.services.print_graph_service import get_graph_png_path

router = APIRouter()
logger = get_logger("GetGraphPNG")

@router.get("")
async def get_graph_png():
    """
    Get the graph visualization as a PNG image.
    Returns the pre-generated PNG file created at startup, or generates it on-demand if not available.
    
    Returns:
        FileResponse: PNG image of the graph diagram.
    """
    logger.info("Get graph PNG endpoint accessed")
    try:
        path = await get_graph_png_path()
        return FileResponse(path, media_type="image/png", filename="graph.png")

    except Exception as e:
        logger.error(f"Error serving graph PNG: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail="Graph PNG not available")