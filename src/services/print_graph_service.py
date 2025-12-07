import os
import re
import subprocess
import tempfile
from src.config.logger import get_logger
from src.graph.graph import build_graph

logger = get_logger("PrintGraphService")

GRAPH_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
GRAPH_PNG_PATH = os.path.join(GRAPH_FOLDER, "graph_diagram.png")


def mermaid_text_to_png_file(input_file: str, output_file: str):
    """
    Converts a Mermaid text file to PNG using Mermaid CLI (mmdc).
    """
    subprocess.run(["mmdc", "-i", input_file, "-o", output_file], check=True)


async def generate_graph_png() -> str:
    """Generate PNG from the graph using Mermaid CLI."""
    graph = build_graph()
    try:
        mermaid_text = graph.get_graph().draw_mermaid()
    except AttributeError:
        mermaid_text = graph.draw_mermaid()

    # ---- Sanitize Mermaid text ----
    mermaid_text = re.sub(r'</?p>', '', mermaid_text)  # remove <p> tags
    mermaid_text = re.sub(r',?\s*line-height:[^;\n]+;?', '', mermaid_text)  # remove line-height
    mermaid_text = re.sub(r'^---[\s\S]*?---\n', '', mermaid_text)  # remove YAML front-matter
    mermaid_text = re.sub(r';\s*$', '', mermaid_text, flags=re.MULTILINE)  # remove semicolons

    # Ensure folder exists
    os.makedirs(GRAPH_FOLDER, exist_ok=True)

    # Write to a temporary .mmd file
    with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as tmp_file:
        tmp_file.write(mermaid_text)
        tmp_path = tmp_file.name

    # Generate PNG
    mermaid_text_to_png_file(tmp_path, GRAPH_PNG_PATH)

    # Clean up temp file
    os.remove(tmp_path)

    logger.info(f"Graph PNG generated: {GRAPH_PNG_PATH}")
    return GRAPH_PNG_PATH


async def get_graph_png_path() -> str:
    """Return the path to the generated PNG, creating it if missing."""
    if not os.path.exists(GRAPH_PNG_PATH):
        logger.info("Graph PNG missing, generating now...")
        await generate_graph_png()
    return GRAPH_PNG_PATH
