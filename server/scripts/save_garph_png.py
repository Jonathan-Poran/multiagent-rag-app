"""
Standalone script to generate a graph PNG without triggering circular imports.
"""

import tempfile
from pathlib import Path
import subprocess

# ---- Paste only the necessary graph build logic here ----
# e.g., your build_graph() function and any minimal node stubs
# You don't need the full server graph import chain.

# Example minimal build_graph() stub
def build_graph_stub():
    from langgraph.graph import StateGraph, END
    from server.graph.state import MessageGraph
    builder = StateGraph(state_schema=MessageGraph)
    builder.set_entry_point("START")
    builder.add_edge("START", END)
    return builder.compile()

desktop_path = Path.home() / "Desktop" / "graph_diagram.png"

def mermaid_to_png_sync(mermaid_text: str, output_path: str):
    """Convert Mermaid diagram to PNG using mmdc."""
    with tempfile.NamedTemporaryFile("w", suffix=".mmd", delete=False) as tmp:
        tmp.write(mermaid_text)
        tmp_path = tmp.name
    try:
        subprocess.run(["mmdc", "-i", tmp_path, "-o", str(output_path)],
                       check=True, capture_output=True, text=True)
        return True
    except Exception as e:
        print(f"Error generating PNG: {e}")
        return False
    finally:
        import os
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def save_graph_to_desktop():
    graph = build_graph_stub()  # use stub instead of full graph import
    mermaid_text = graph.get_graph().draw_mermaid()
    if not mermaid_text:
        print("Graph Mermaid diagram is empty")
        return
    success = mermaid_to_png_sync(mermaid_text, desktop_path)
    if success:
        print(f"Graph PNG saved to: {desktop_path}")
    else:
        print("Failed to generate graph PNG")

if __name__ == "__main__":
    save_graph_to_desktop()
