import os
import subprocess
import tempfile
from src.config.logger import get_logger
from src.graph.graph import build_graph

logger = get_logger("PrintGraphService")

# Use /tmp on AWS EB
GRAPH_SVG_PATH = os.path.join(tempfile.gettempdir(), "graph_diagram.svg")

def ensure_mermaid_cli() -> str:
    """Ensure Mermaid CLI is installed."""
    for cmd in ["mmdc", "/usr/local/bin/mmdc", "/usr/bin/mmdc"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            logger.info(f"Found mermaid-cli at {cmd}")
            return cmd
        except Exception:
            continue
    raise RuntimeError("mermaid-cli not found")

def generate_graph_svg() -> str:
    """Generate SVG instead of PNG."""
    graph = build_graph()
    try:
        mermaid_text = graph.get_graph().draw_mermaid()
    except AttributeError:
        mermaid_text = graph.draw_mermaid()

    if not mermaid_text.strip():
        raise ValueError("Graph Mermaid text is empty")

    os.makedirs(os.path.dirname(GRAPH_SVG_PATH), exist_ok=True)

    cmd = ensure_mermaid_cli()
    subprocess.run(
        [cmd, "-i", "-", "-o", GRAPH_SVG_PATH],
        input=mermaid_text.encode("utf-8"),
        check=True,
        timeout=30
    )
    logger.info(f"Graph SVG generated: {GRAPH_SVG_PATH}")
    return GRAPH_SVG_PATH

def get_graph_svg_path() -> str:
    if not os.path.exists(GRAPH_SVG_PATH):
        logger.info("Graph SVG missing, generating now...")
        generate_graph_svg()
    return GRAPH_SVG_PATH
