"""Base generator class for text2api generators."""
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class BaseGenerator(ABC):
    """Base class for all generators in text2api."""

    def __init__(self, output_dir: str = "generated_apis"):
        """Initialize the generator with output directory.
        
        Args:
            output_dir: Base directory where generated files will be saved
        """
        self.output_dir = output_dir
        self.template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "generators",
            "templates"
        )
        self.project_name: str = ""
        self.api_spec: Dict[str, Any] = {}

    def set_project_name(self, name: str) -> None:
        """Set the project name for the generated API.
        
        Args:
            name: Name of the project/API
        """
        self.project_name = name.lower().replace(" ", "_")

    def set_api_spec(self, spec: Dict[str, Any]) -> None:
        """Set the API specification.
        
        Args:
            spec: Dictionary containing the API specification
        """
        self.api_spec = spec

    def ensure_output_dir(self) -> str:
        """Ensure the output directory exists.
        
        Returns:
            str: Path to the project-specific output directory
        """
        if not self.project_name:
            raise ValueError("Project name must be set before generating output")
            
        project_dir = os.path.join(self.output_dir, self.project_name)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir

    @abstractmethod
    def generate(self, **kwargs) -> str:
        """Generate the API components.
        
        Returns:
            str: Path to the generated files or success message
        """
        pass

    def _write_file(self, path: str, content: str) -> None:
        """Helper method to write content to a file.
        
        Args:
            path: Relative path where the file should be written
            content: Content to write to the file
        """
        output_path = os.path.join(self.output_dir, self.project_name, path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return output_path
