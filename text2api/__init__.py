"""Text2API - Automatyczne generowanie API na podstawie opisu tekstowego."""

__version__ = "0.1.3"

# Import main components to make them available at package level
from .cli import cli

__all__ = ["cli"]
