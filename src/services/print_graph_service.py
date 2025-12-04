"""
Service for generating graph PNG images.
Handles the heavy lifting of Mermaid diagram conversion.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from src.config.logger import get_logger

logger = get_logger("PrintGraph")

# Store the path to the pre-generated PNG file (set at startup)
_graph_png_path: str | None = None


def mermaid_to_png_sync(mermaid_text: str, output_path: str) -> bool:
    """
    Convert Mermaid diagram text to PNG image (synchronous version).
    
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


def generate_graph_png_at_startup(output_path: str = None) -> str:
    """
    Generate the graph PNG at server startup.
    This should be called during server initialization.
    Stores the path globally so the API can access it.
    
    Args:
        output_path: Optional custom path for the PNG. If None, uses temp directory.
    
    Returns:
        str: Path to the generated PNG file, or None if generation failed.
    """
    global _graph_png_path
    
    # Lazy import to avoid circular dependencies
    from src.graph.graph import graph
    
    if graph is None:
        logger.warning("Graph is not initialized, cannot generate PNG")
        return None
    
    try:
        # Get mermaid diagram text
        mermaid_diagram = graph.get_graph().draw_mermaid()
        
        if not mermaid_diagram:
            logger.warning("Mermaid diagram text is empty, cannot generate PNG")
            return None
        
        # Use provided path or default to temp directory
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "graph_diagram.png")
        
        # Generate PNG
        if mermaid_to_png_sync(mermaid_diagram, output_path):
            _graph_png_path = output_path
            logger.info(f"Graph PNG generated successfully at startup: {_graph_png_path}")
            return _graph_png_path
        else:
            logger.error("Failed to generate graph PNG at startup")
            return None
    except Exception as e:
        logger.error(f"Error generating graph PNG at startup: {e}", exc_info=True)
        return None


def get_graph_png_path() -> str | None:
    """
    Get the path to the pre-generated graph PNG file.
    Returns None if the PNG was not generated at startup.
    
    Returns:
        str | None: Path to the PNG file, or None if not generated.
    """
    return _graph_png_path


def generate_graph_png_on_demand(output_path: str = None) -> str:
    """
    Generate the graph PNG on demand.
    
    Args:
        output_path: Optional custom path for the PNG. If None, uses temp directory.
    
    Returns:
        str: Path to the generated PNG file, or None if generation failed.
    """
    # Lazy import to avoid circular dependencies
    from src.graph.graph import graph
    
    if graph is None:
        raise ValueError("Graph is not initialized")
    
    try:
        # Get mermaid diagram text
        mermaid_diagram = graph.get_graph().draw_mermaid()
        
        if not mermaid_diagram:
            raise ValueError("Mermaid diagram text is empty")
        
        # Use provided path or default to temp directory
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "graph_diagram.png")
        
        # Generate PNG
        if mermaid_to_png_sync(mermaid_diagram, output_path):
            logger.info(f"Graph PNG generated on demand: {output_path}")
            return output_path
        else:
            raise RuntimeError("Failed to generate PNG")
    except Exception as e:
        logger.error(f"Error generating graph PNG on demand: {e}", exc_info=True)
        raise

