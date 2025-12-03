"""
Pytest configuration for server tests.
Adds project root to Python path for imports.
"""

import sys
import os
from pathlib import Path

# Get the project root (3 levels up from this file: server/tests/conftest.py)
project_root = Path(__file__).parent.parent.parent.absolute()

# Add project root to Python path if not already there
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also set PYTHONPATH environment variable for subprocesses
os.environ.setdefault('PYTHONPATH', str(project_root))

