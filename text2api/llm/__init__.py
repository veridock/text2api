
"""
LLM integration module
"""

from .ollama_client import OllamaClient, OllamaModel
from .language_detector import LanguageDetector

__all__ = [
    'OllamaClient',
    'OllamaModel',
    'LanguageDetector'
]
