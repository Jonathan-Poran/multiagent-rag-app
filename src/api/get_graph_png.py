import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from src.config.logger import get_logger
from src.services.print_graph_service import get_graph_png_path, generate_graph_png_on_demand

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
    # Get the path from the service (where it was stored at startup)
    graph_png_path = get_graph_png_path()
    
    # If no startup PNG exists or file is missing, generate on-demand
    if graph_png_path is None or not os.path.exists(graph_png_path):
        if graph_png_path is None:
            logger.info("Graph PNG was not generated at startup. Generating on-demand...")
        else:
            logger.warning(f"Graph PNG file not found at expected path: {graph_png_path}. Generating on-demand...")
        
        try:
            # Generate PNG on-demand
            graph_png_path = generate_graph_png_on_demand()
            logger.info(f"Successfully generated graph PNG on-demand: {graph_png_path}")
        except Exception as e:
            logger.error(f"Failed to generate graph PNG on-demand: {e}", exc_info=True)
            raise HTTPException(
                status_code=503,
                detail=f"Failed to generate graph PNG. Please check server logs. Error: {str(e)}"
            )
    
    # Return the PNG file
    return FileResponse(
        graph_png_path,
        media_type="image/png",
        filename="app_graph.png"
    )

