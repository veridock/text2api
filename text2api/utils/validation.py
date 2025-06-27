"""
Walidacja i sprawdzanie konfiguracji
"""

import re
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


def validate_api_name(name: str) -> bool:
    """Waliduje nazwę API"""
    if not name:
        return False

    # Nazwa może zawierać tylko litery, cyfry i podkreślniki
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name))


def validate_endpoint_path(path: str) -> bool:
    """Waliduje ścieżkę endpointu"""
    if not path.startswith("/"):
        return False

    # Podstawowa walidacja ścieżki REST
    return bool(re.match(r"^/[a-zA-Z0-9/_{}:-]*$", path))


def validate_field_type(field_type: str) -> bool:
    """Waliduje typ pola"""
    valid_types = {
        "string",
        "integer",
        "float",
        "boolean",
        "datetime",
        "date",
        "time",
        "array",
        "object",
    }
    return field_type in valid_types


def validate_http_method(method: str) -> bool:
    """Waliduje metodę HTTP"""
    valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
    return method.upper() in valid_methods


def validate_project_name(name: str) -> bool:
    """Waliduje nazwę projektu"""
    if not name or len(name) < 2 or len(name) > 50:
        return False

    # Nazwa projektu może zawierać litery, cyfry, myślniki i podkreślniki
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name))


def validate_environment() -> Dict[str, Any]:
    """Sprawdza środowisko i zależności"""

    result = {"valid": True, "errors": [], "warnings": [], "info": []}

    # Sprawdź Python version
    import sys

    python_version = sys.version_info
    if python_version < (3, 9):
        result["errors"].append(
            f"Python 3.9+ required, found {python_version.major}.{python_version.minor}"
        )
        result["valid"] = False
    else:
        result["info"].append(
            f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

    # Sprawdź dostępność Ollama
    try:
        import httpx
        import asyncio

        async def check_ollama():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "http://localhost:11434/api/tags", timeout=5
                    )
                    return response.status_code == 200
            except:
                return False

        # Nie można uruchomić async w synchronicznym kontekście tutaj
        # To będzie sprawdzone w czasie rzeczywistym
        result["info"].append("Ollama status will be checked during generation")

    except ImportError:
        result["warnings"].append("httpx not available - cannot check Ollama status")

    # Sprawdź Docker
    try:
        import docker

        docker_client = docker.from_env()
        docker_client.ping()
        result["info"].append("Docker is available")
    except:
        result["warnings"].append(
            "Docker not available - containerization features disabled"
        )

    # Sprawdź uprawnienia do zapisu
    try:
        test_dir = Path("./generated_apis")
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        result["info"].append("Write permissions OK")
    except PermissionError:
        result["errors"].append("No write permissions in current directory")
        result["valid"] = False

    return result


def sanitize_filename(filename: str) -> str:
    """Czyści nazwę pliku z niebezpiecznych znaków"""

    # Usuń niebezpieczne znaki
    filename = re.sub(r'[<>:"/\\|?*]', "", filename)

    # Zastąp spacje podkreślnikami
    filename = re.sub(r"\s+", "_", filename)

    # Usuń wielokrotne podkreślniki
    filename = re.sub(r"_+", "_", filename)
