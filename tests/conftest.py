"""
Pytest configuration for tests.
Adds project root to Python path for imports.
"""

import sys
import os
import warnings
from pathlib import Path

# Get the project root (1 level up from this file: tests/conftest.py)
project_root = Path(__file__).parent.parent.absolute()

# Add project root to Python path if not already there
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Also set PYTHONPATH environment variable for subprocesses
os.environ.setdefault('PYTHONPATH', str(project_root))

# Suppress Pydantic deprecation warnings in tests only
import pytest

def pytest_configure(config):
    """Configure pytest to ignore Pydantic deprecation warnings."""
    config.addinivalue_line(
        "filterwarnings",
        "ignore::pydantic.warnings.PydanticDeprecatedSince20"
    )

