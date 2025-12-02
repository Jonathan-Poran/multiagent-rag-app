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


async def mermaid_to_png(mermaid_text: str):
    """
    Convert Mermaid diagram text to PNG image.
    
    Args:
        mermaid_text: The Mermaid diagram text to convert.
    
    Returns:
        FileResponse: PNG image file response.
    
    Raises:
        HTTPException: If PNG generation fails.
    """
    # Check if mmdc is available
    try:
        subprocess.run(["mmdc", "--version"], capture_output=True, check=True, timeout=5)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        logger.error("mermaid-cli (mmdc) is not installed or not in PATH")
        raise HTTPException(
            status_code=503,
            detail="mermaid-cli is not installed. Please install it with: npm install -g @mermaid-js/mermaid-cli"
        )
    
    if not mermaid_text or not mermaid_text.strip():
        raise HTTPException(status_code=400, detail="Mermaid diagram text is empty")
    
    # Create a temporary file for input and output
    with tempfile.NamedTemporaryFile(suffix=".mmd", delete=False, mode='w', encoding='utf-8') as tmp_input:
        tmp_input.write(mermaid_text)
        input_path = tmp_input.name
    
    output_path = input_path + ".png"
    
    try:
        logger.info(f"Generating PNG from Mermaid diagram (input: {input_path}, output: {output_path})")
        
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
            raise HTTPException(status_code=500, detail=error_msg)
        
        logger.info(f"Successfully generated PNG from Mermaid diagram at {output_path}")
        
        # Return FileResponse - file will be served and cleaned up by OS temp cleanup
        return FileResponse(
            output_path,
            media_type="image/png",
            filename="diagram.png"
        )
    except subprocess.CalledProcessError as e:
        error_msg = f"mmdc failed: stdout={e.stdout}, stderr={e.stderr}"
        logger.error(f"Failed to generate PNG: {error_msg}")
        # Clean up on error
        if os.path.exists(input_path):
            os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise HTTPException(status_code=500, detail=f"Failed to generate PNG: {error_msg}")
    except subprocess.TimeoutExpired:
        error_msg = "mmdc command timed out after 30 seconds"
        logger.error(error_msg)
        # Clean up on error
        if os.path.exists(input_path):
            os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        logger.error(f"Unexpected error generating PNG: {e}", exc_info=True)
        # Clean up on error
        if os.path.exists(input_path):
            os.unlink(input_path)
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise HTTPException(status_code=500, detail=f"Failed to generate PNG: {str(e)}")
    finally:
        # Clean up input file immediately (output will be cleaned after response)
        if os.path.exists(input_path):
            try:
                os.unlink(input_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup input file: {e}")


@router.get("")
async def get_graph():
    """
    Get the graph visualization as a PNG image.
    
    Returns:
        FileResponse: PNG image of the graph diagram.
    """
    if graph is None:
        raise HTTPException(status_code=503, detail="Graph is not initialized")
    
    try:
        # Get mermaid diagram text
        mermaid_diagram = graph.get_graph().draw_mermaid()
        logger.info(f"Retrieved Mermaid diagram text (length: {len(mermaid_diagram) if mermaid_diagram else 0})")
        
        if not mermaid_diagram:
            raise HTTPException(status_code=500, detail="Mermaid diagram text is empty")
        
        # Convert to PNG
        return await mermaid_to_png(mermaid_diagram)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error generating graph PNG: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating graph PNG: {str(e)}")