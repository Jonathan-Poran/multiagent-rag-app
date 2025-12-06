# src/services/graph_service.py
import os
import subprocess
import tempfile
from pathlib import Path
from src.config.logger import get_logger
from src.graph.graph import build_graph

logger = get_logger("GraphService")


# Use /tmp for AWS EB (writable), fallback to static folder locally
if os.environ.get("AWS_EB_ENV"):
    GRAPH_PNG_PATH = os.path.join(tempfile.gettempdir(), "graph_diagram.png")
else:
    GRAPH_PNG_PATH = os.path.join(os.path.dirname(__file__), "../../static/graph.png")


def ensure_mermaid_cli() -> str:
    """
    Ensure Mermaid CLI is installed and return the command path.
    """
    for cmd in ["mmdc", "/usr/local/bin/mmdc", "/usr/bin/mmdc"]:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, check=True)
            logger.info(f"Found mermaid-cli at {cmd}: {result.stdout.decode().strip()}")
            return cmd
        except Exception:
            continue
    logger.error("mermaid-cli (mmdc) not found. Please install it in the environment.")
    raise RuntimeError("mermaid-cli not found")


def generate_graph_png() -> str:
    """
    Generate the PNG for the graph and store it in the appropriate folder.
    Returns the path to the PNG.
    """
    graph = build_graph()
    try:
        mermaid_text = graph.get_graph().draw_mermaid()
    except AttributeError:
        mermaid_text = graph.draw_mermaid()

    if not mermaid_text.strip():
        raise ValueError("Graph Mermaid text is empty")

    os.makedirs(os.path.dirname(GRAPH_PNG_PATH), exist_ok=True)

    cmd = ensure_mermaid_cli()
    try:
        subprocess.run(
            [cmd, "-i", "-", "-o", GRAPH_PNG_PATH],
            input=mermaid_text.encode("utf-8"),
            check=True,
            timeout=30
        )
        if not os.path.exists(GRAPH_PNG_PATH):
            raise RuntimeError("Failed to create PNG")
        logger.info(f"Graph PNG generated: {GRAPH_PNG_PATH}")
        return GRAPH_PNG_PATH
    except Exception as e:
        logger.error(f"Failed to generate graph PNG: {e}", exc_info=True)
        raise


def get_graph_png_path() -> str:
    """
    Return the PNG path, generating it on demand if missing.
    """
    if not os.path.exists(GRAPH_PNG_PATH):
        logger.info("Graph PNG missing, generating now...")
        generate_graph_png()
    return GRAPH_PNG_PATH