import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from server.config.logger import get_logger
from server.services.print_graph import generate_graph_png_at_startup, generate_graph_png_on_demand

router = APIRouter()
logger = get_logger("GetGraphPNG")

# Store the path to the pre-generated PNG file
_graph_png_path: str | None = None


def initialize_graph_png():
    """
    Initialize the graph PNG at server startup.
    This should be called during server initialization.
    """
    global _graph_png_path
    _graph_png_path = generate_graph_png_at_startup()


@router.get("")
async def get_graph_png():
    """
    Get the graph visualization as a PNG image.
    Returns the pre-generated PNG file created at startup, or generates it on-demand.
    
    Returns:
        FileResponse: PNG image of the graph diagram.
    """
    global _graph_png_path
    
    # If PNG doesn't exist or wasn't generated at startup, generate it on-demand
    if _graph_png_path is None or not os.path.exists(_graph_png_path):
        try:
            _graph_png_path = generate_graph_png_on_demand()
        except ValueError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Error generating graph PNG on-demand: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating graph PNG: {str(e)}")
    
    # Return the pre-generated file
    return FileResponse(
        _graph_png_path,
        media_type="image/png",
        filename="app_graph.png"
    )

