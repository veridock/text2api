"""
Text2API - A tool for automatically generating APIs from text descriptions using NLP.
"""

__version__ = "0.1.5"

# Import the main CLI function for easier access
from .cli import main as cli

__all__ = ["cli", "__version__"]
