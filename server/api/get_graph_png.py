import os
import subprocess
import tempfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from server.graph.graph import graph
from server.config.logger import get_logger

router = APIRouter()
logger = get_logger("GetGraphPNG")

# Store the path to the pre-generated PNG file
_graph_png_path: str | None = None


def mermaid_to_png_sync(mermaid_text: str, output_path: str) -> bool:
    """
    Convert Mermaid diagram text to PNG image (synchronous version for startup).
    
    Args:
        mermaid_text: The Mermaid diagram text to convert.
        output_path: Path where the PNG should be saved.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    # Check if mmdc is available
    try:
        subprocess.run(["mmdc", "--version"], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.error(f"mermaid-cli (mmdc) is not installed or not in PATH: {e}")
        return False
    
    if not mermaid_text or not mermaid_text.strip():
        logger.error("Mermaid diagram text is empty")
        return False
    
    # Create a temporary file for input
    with tempfile.NamedTemporaryFile(suffix=".mmd", delete=False, mode='w', encoding='utf-8') as tmp_input:
        tmp_input.write(mermaid_text)
        input_path = tmp_input.name
    
    try:
        logger.info(f"Generating PNG from Mermaid diagram \n input: {input_path} \n output: {output_path}")
        
        # Run mermaid-cli with timeout
        result = subprocess.run(
            ["mmdc", "-i", input_path, "-o", output_path],
            check=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if not os.path.exists(output_path):
            error_msg = f"PNG file was not created. mmdc stdout: {result.stdout}, stderr: {result.stderr}"
            logger.error(error_msg)
            return False
        
        logger.info(f"Successfully generated graph PNG")
        return True
    except subprocess.CalledProcessError as e:
        error_msg = f"mmdc failed: stdout={e.stdout}, stderr={e.stderr}"
        logger.error(f"Failed to generate PNG: {error_msg}")
        return False
    except subprocess.TimeoutExpired:
        error_msg = "mmdc command timed out after 30 seconds"
        logger.error(error_msg)
        return False
    except Exception as e:
        logger.error(f"Unexpected error generating PNG: {e}", exc_info=True)
        return False
    finally:
        # Clean up input file
        if os.path.exists(input_path):
            try:
                os.unlink(input_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup input file: {e}")


def generate_graph_png_at_startup():
    """
    Generate the graph PNG at server startup.
    This should be called during server initialization.
    """
    global _graph_png_path
    
    if graph is None:
        logger.warning("Graph is not initialized, cannot generate PNG")
        return
    
    try:
        # Get mermaid diagram text
        mermaid_diagram = graph.get_graph().draw_mermaid()
        
        if not mermaid_diagram:
            logger.warning("Mermaid diagram text is empty, cannot generate PNG")
            return
        
        # Use a persistent location for the PNG file
        # Store in a temp directory that persists for the container lifetime
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, "graph_diagram.png")
        
        # Generate PNG
        if mermaid_to_png_sync(mermaid_diagram, output_path):
            _graph_png_path = output_path
            logger.info(f"Graph PNG generated successfully at startup: {_graph_png_path}")
        else:
            logger.error("Failed to generate graph PNG at startup")
    except Exception as e:
        logger.error(f"Error generating graph PNG at startup: {e}", exc_info=True)


@router.get("")
async def get_graph():
    """
    Get the graph visualization as a PNG image.
    Returns the pre-generated PNG file created at startup.
    
    Returns:
        FileResponse: PNG image of the graph diagram.
    """
    global _graph_png_path
    
    if _graph_png_path is None or not os.path.exists(_graph_png_path):
        # Try to generate it on-demand if not available
        if graph is None:
            raise HTTPException(status_code=503, detail="Graph is not initialized")
        
        try:
            mermaid_diagram = graph.get_graph().draw_mermaid()
            if not mermaid_diagram:
                raise HTTPException(status_code=500, detail="Mermaid diagram text is empty")
            
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "graph_diagram.png")
            
            if mermaid_to_png_sync(mermaid_diagram, output_path):
                _graph_png_path = output_path
            else:
                raise HTTPException(status_code=500, detail="Failed to generate PNG")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating graph PNG on-demand: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error generating graph PNG: {str(e)}")
    
    # Return the pre-generated file
    return FileResponse(
        _graph_png_path,
        media_type="image/png",
        filename="app_graph.png"
    )

