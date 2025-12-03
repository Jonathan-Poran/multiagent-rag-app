"""
Script to generate and save the graph PNG to desktop.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Hardcoded desktop path (macOS)
desktop_path = Path.home() / "Desktop" / "graph_diagram.png"


def save_graph_to_desktop():
    """Generate graph PNG and save it to desktop."""
    try:
        # Use the service to generate the PNG
        from server.services.print_graph import generate_graph_png_on_demand
        
        print(f"Generating graph PNG...")
        print(f"Output path: {desktop_path}")
        
        # Generate PNG using the service
        result_path = generate_graph_png_on_demand(str(desktop_path))
        
        if result_path:
            print(f"✓ Successfully saved graph PNG to: {desktop_path}")
            return True
        else:
            print("✗ Failed to generate PNG")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = save_graph_to_desktop()
    sys.exit(0 if success else 1)
