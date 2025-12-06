import os
import subprocess
import tempfile
from src.config.logger import get_logger

logger = get_logger("PrintGraphService")

# Always use /tmp in EB for writable folder
GRAPH_PNG_PATH = os.path.join(tempfile.gettempdir(), "graph_diagram.png")


def ensure_mermaid_cli() -> str:
    for cmd in ["mmdc", "/usr/local/bin/mmdc", "/usr/bin/mmdc"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            logger.info(f"Found mermaid-cli at {cmd}")
            return cmd
        except Exception:
            continue
    logger.error("mermaid-cli not found")
    raise RuntimeError("mermaid-cli not found")


def generate_graph_png() -> str:
    from src.graph.graph import build_graph
    graph = build_graph()
    try:
        mermaid_text = graph.get_graph().draw_mermaid()
    except AttributeError:
        mermaid_text = graph.draw_mermaid()

    if not mermaid_text.strip():
        raise ValueError("Graph Mermaid text is empty")

    os.makedirs(os.path.dirname(GRAPH_PNG_PATH), exist_ok=True)

    cmd = ensure_mermaid_cli()
    subprocess.run([cmd, "-i", "-", "-o", GRAPH_PNG_PATH],
                   input=mermaid_text.encode("utf-8"),
                   check=True,
                   timeout=30)
    logger.info(f"Graph PNG generated at {GRAPH_PNG_PATH}")
    return GRAPH_PNG_PATH


def get_graph_png_path() -> str:
    if not os.path.exists(GRAPH_PNG_PATH):
        logger.info("Graph PNG missing, generating now...")
        generate_graph_png()
    return GRAPH_PNG_PATH
