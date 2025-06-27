"""
API Generator Module

This module contains the main APIGenerator class responsible for generating
API projects based on natural language descriptions.
"""
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

from ..llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class APIGenerator:
    """
    Main class for generating API projects from natural language descriptions.

    This class handles the complete pipeline from natural language processing
    to code generation for different API types and frameworks.
    """

    def __init__(
        self, output_dir: str = "./generated_apis", ollama_url: Optional[str] = None
    ):
        """
        Initialize the APIGenerator.

        Args:
            output_dir: Directory where generated projects will be saved
            ollama_url: URL of the Ollama server (optional)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ollama_client = OllamaClient(base_url=ollama_url) if ollama_url else None

    async def generate(
        self,
        description: str,
        api_type: str = "rest",
        framework: str = "fastapi",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate an API project from a natural language description.

        Args:
            description: Natural language description of the desired API
            api_type: Type of API to generate (rest, graphql, grpc, websocket, cli)
            framework: Target framework (fastapi, flask, etc.)
            **kwargs: Additional options for code generation

        Returns:
            Dict containing generation results and metadata
        """
        logger.info(f"Generating {api_type.upper()} API with {framework}")

        if not self.validate_description(description):
            return {
                "status": "error",
                "error": "Invalid description. Please provide a more detailed description.",
            }

        # Use Ollama for code generation if available
        if self.ollama_client:
            try:
                # TODO: Implement actual code generation with Ollama
                # This is a placeholder implementation
                prompt = f"""Generate a {framework} {api_type} API based on the following description:
                
                {description}
                
                Please provide the code structure and implementation details."""

                # Generate code using Ollama
                response = await self.ollama_client.generate(
                    model="llama3.1:8b",  # Default model, can be made configurable
                    prompt=prompt,
                    format="json",
                )

                # Process the response and generate files
                # This is a simplified example - actual implementation would parse the response
                # and generate appropriate files based on the API type and framework

                result = {
                    "status": "success",
                    "api_type": api_type,
                    "framework": framework,
                    "project_dir": str(self.output_dir / f"{api_type}_{framework}_api"),
                    "files_generated": ["main.py", "requirements.txt"],
                    "message": "API generated successfully with Ollama",
                }

            except Exception as e:
                logger.error(f"Error generating API with Ollama: {str(e)}")
                return {
                    "status": "error",
                    "error": f"Failed to generate API with Ollama: {str(e)}",
                }
        else:
            # Fallback to basic template generation if Ollama is not available
            result = {
                "status": "success",
                "api_type": api_type,
                "framework": framework,
                "project_dir": str(self.output_dir / "example_project"),
                "files_generated": ["main.py", "requirements.txt"],
                "message": "Basic API template generated (Ollama not configured)",
            }

        return result

    def validate_description(self, description: str) -> bool:
        """
        Validate if the description is suitable for API generation.

        Args:
            description: The description to validate

        Returns:
            bool: True if description is valid, False otherwise
        """
        if not description or not description.strip():
            return False
        return len(description.split()) >= 3  # At least 3 words required

    def list_supported_frameworks(self) -> Dict[str, list]:
        """
        List all supported API types and frameworks.

        Returns:
            Dict mapping API types to lists of supported frameworks
        """
        return {
            "rest": ["fastapi", "flask", "django"],
            "graphql": ["strawberry", "graphene"],
            "grpc": ["grpcio"],
            "websocket": ["fastapi", "aiohttp"],
            "cli": ["click", "typer"],
        }


# For backward compatibility
__all__ = ["APIGenerator"]
