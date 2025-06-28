"""OpenAPI generator for text2api."""
import os
import json
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader
from .base_generator import BaseGenerator


class OpenAPIGenerator(BaseGenerator):
    """Generates OpenAPI specifications from API descriptions."""

    def __init__(self, output_dir: str = "generated_apis"):
        """Initialize the OpenAPI generator.
        
        Args:
            output_dir: Base directory where generated files will be saved
        """
        super().__init__(output_dir)
        self.template_dir = os.path.join(self.template_dir, "openapi")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def _generate_models(self) -> Dict[str, Any]:
        """Generate OpenAPI components for models.
        
        Returns:
            Dict with OpenAPI components for models
        """
        components = {"schemas": {}}
        
        # Default models if not provided in spec
        if "models" not in self.api_spec:
            self.api_spec["models"] = [
                {"name": "Item", "fields": ["id", "name", "description"]}
            ]
            
        for model in self.api_spec.get("models", []):
            model_name = model["name"]
            components["schemas"][model_name] = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            # Add fields to the model
            for field in model.get("fields", []):
                field_name = field["name"] if isinstance(field, dict) else field
                field_type = field.get("type", "string") if isinstance(field, dict) else "string"
                
                # Map Python types to OpenAPI types
                type_mapping = {
                    "str": "string",
                    "int": "integer",
                    "float": "number",
                    "bool": "boolean",
                    "datetime": "string"
                }
                
                openapi_type = type_mapping.get(field_type.lower(), "string")
                field_spec = {"type": openapi_type}
                
                # Add format for certain types
                if openapi_type == "string" and field_type.lower() in ["date", "datetime"]:
                    field_spec["format"] = field_type.lower()
                
                components["schemas"][model_name]["properties"][field_name] = field_spec
                
                # Mark required fields
                if isinstance(field, dict) and field.get("required", False):
                    components["schemas"][model_name]["required"].append(field_name)
        
        return components

    def _generate_paths(self) -> Dict[str, Any]:
        """Generate OpenAPI paths for the API.
        
        Returns:
            Dict with OpenAPI paths
        """
        paths = {}
        
        # Generate CRUD endpoints for each model
        for model in self.api_spec.get("models", []):
            model_name = model["name"]
            model_name_lower = model_name.lower()
            
            # Collection endpoints
            paths[f'/{model_name_lower}'] = {
                "get": {
                    "summary": f"List all {model_name} items",
                    "responses": {
                        "200": {
                            "description": f"A list of {model_name} items",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": f"#/components/schemas/{model_name}"}
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": f"Create a new {model_name}",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{model_name}"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": f"Created {model_name}",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": f"#/components/schemas/{model_name}"}
                                }
                            }
                        }
                    }
                }
            }
            
            # Item endpoints
            paths[f'/{model_name_lower}/{{{model_name_lower}_id}}'] = {
                "get": {
                    "summary": f"Get a {model_name} by ID",
                    "parameters": [
                        {
                            "name": f"{model_name_lower}_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": f"The {model_name} item",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": f"#/components/schemas/{model_name}"}
                                }
                            }
                        }
                    }
                },
                "put": {
                    "summary": f"Update a {model_name} by ID",
                    "parameters": [
                        {
                            "name": f"{model_name_lower}_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": f"#/components/schemas/{model_name}"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": f"Updated {model_name}",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": f"#/components/schemas/{model_name}"}
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "summary": f"Delete a {model_name} by ID",
                    "parameters": [
                        {
                            "name": f"{model_name_lower}_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "204": {
                            "description": f"{model_name} deleted"
                        }
                    }
                }
            }
        
        return paths

    def generate(self, **kwargs) -> str:
        """Generate OpenAPI specification.
        
        Args:
            **kwargs: Additional keyword arguments
            
        Returns:
            str: Path to the generated OpenAPI specification file
        """
        if not self.project_name:
            raise ValueError("Project name must be set before generating OpenAPI spec")
            
        # Generate components and paths
        components = self._generate_models()
        paths = self._generate_paths()
        
        # Create the full OpenAPI spec
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.api_spec.get("name", self.project_name.replace("_", " ").title()),
                "description": self.api_spec.get("description", ""),
                "version": "1.0.0"
            },
            "paths": paths,
            "components": components
        }
        
        # Ensure output directory exists
        output_dir = self.ensure_output_dir()
        
        # Write the OpenAPI spec to a file
        output_file = os.path.join(output_dir, "openapi.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_spec, f, indent=2)
            
        return output_file
