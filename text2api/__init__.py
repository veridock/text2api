"""
text2api - Automatyczne generowanie API z opisu tekstowego

Biblioteka wykorzystująca NLP i Ollama do inteligentnego generowania
kompletnych projektów API na podstawie opisów w języku naturalnym.
"""

__version__ = "0.1.0"
__author__ = "text2api Team"
__email__ = "team@text2api.dev"
__description__ = "Automatyczne generowanie API z opisu tekstowego używając NLP i Ollama"

# Główne klasy i funkcje
from .core.generator import APIGenerator
from .core.analyzer import TextAnalyzer, ApiSpec, ApiType
from .llm.ollama_client import OllamaClient
from .cli import main as cli_main

# Convenience imports
from .examples.sample_descriptions import (
    SAMPLE_DESCRIPTIONS,
    get_random_description,
    get_examples_by_api_type
)

# Wersja API
API_VERSION = "v1"

__all__ = [
    "APIGenerator",
    "TextAnalyzer",
    "ApiSpec",
    "ApiType",
    "OllamaClient",
    "cli_main",
    "SAMPLE_DESCRIPTIONS",
    "get_random_description",
    "get_examples_by_api_type",
    "__version__"
]

# Sprawdź podstawowe zależności przy imporcie
try:
    import ollama
    import jinja2
    import click
    import rich
    DEPENDENCIES_OK = True
except ImportError as e:
    DEPENDENCIES_OK = False
    _missing_dep = str(e)

def check_dependencies():
    """Sprawdza czy wszystkie zależności są dostępne"""
    if not DEPENDENCIES_OK:
        raise ImportError(
            f"Brakuje wymaganych zależności: {_missing_dep}\n"
            "Uruchom: pip install text2api[all]"
        )
    return True

# Banner dla CLI
BANNER = f"""
╔══════════════════════════════════════════════════════════════╗
║                    text2api v{__version__}                   ║
║                                                              ║
║        🤖 Automatyczne generowanie API z opisu tekstowego    ║
║           📝 NLP → 🔧 Kod → 🐳 Docker → 🚀 Deploy             ║
╚══════════════════════════════════════════════════════════════╝
"""