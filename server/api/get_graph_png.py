import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from server.config.logger import get_logger
from server.services.print_graph import get_graph_png_path

router = APIRouter()
logger = get_logger("GetGraphPNG")

@router.get("")
async def get_graph_png():
    """
    Get the graph visualization as a PNG image.
    Returns the pre-generated PNG file created at startup.
    
    Returns:
        FileResponse: PNG image of the graph diagram.
    """
    # Get the path from the service (where it was stored at startup)
    graph_png_path = get_graph_png_path()
    
    if graph_png_path is None:
        raise HTTPException(
            status_code=503, 
            detail="Graph PNG was not generated at startup. Please check server logs."
        )
    
    if not os.path.exists(graph_png_path):
        logger.warning(f"Graph PNG file not found at expected path: {graph_png_path}")
        raise HTTPException(
            status_code=404,
            detail="Graph PNG file not found. It may have been deleted or not generated correctly."
        )
    
    # Return the pre-generated file
    return FileResponse(
        graph_png_path,
        media_type="image/png",
        filename="app_graph.png"
    )

