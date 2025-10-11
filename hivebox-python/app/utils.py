"""Utility functions for the HiveBox application."""
from pathlib import Path


def get_project_root() -> Path:
    """
    Get the project root directory (hivebox-python/).
    Returns the parent directory of the app/ directory.
    """
    return Path(__file__).parent.parent
