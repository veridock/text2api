"""
API Generator Module

This module contains the main APIGenerator class responsible for generating
API projects based on natural language descriptions.
"""
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class APIGenerator:
    """
    Main class for generating API projects from natural language descriptions.
    
    This class handles the complete pipeline from natural language processing
    to code generation for different API types and frameworks.
    """
    
    def __init__(self, output_dir: str = "./generated_apis"):
        """
        Initialize the APIGenerator.
        
        Args:
            output_dir: Directory where generated projects will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(self, description: str, api_type: str = "rest", 
                framework: str = "fastapi", **kwargs) -> Dict[str, Any]:
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
        
        # TODO: Implement actual code generation logic
        # This is a placeholder implementation
        result = {
            "status": "success",
            "api_type": api_type,
            "framework": framework,
            "project_dir": str(self.output_dir / "example_project"),
            "files_generated": []
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
            "cli": ["click", "typer"]
        }

# For backward compatibility
__all__ = ['APIGenerator']
