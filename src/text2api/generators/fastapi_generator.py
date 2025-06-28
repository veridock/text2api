"""FastAPI server generator for text2api."""
import os
import shutil
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from .base_generator import BaseGenerator


class FastAPIGenerator(BaseGenerator):
    """Generates FastAPI server code from API specifications."""

    def __init__(self, output_dir: str = "generated_apis"):
        """Initialize the FastAPI generator.
        
        Args:
            output_dir: Base directory where generated files will be saved
        """
        super().__init__(output_dir)
        
        # Get the directory where the current file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Path to the templates directory relative to this file
        self.template_dir = os.path.join(current_dir, 'templates', 'fastapi')
        
        # Create the template environment
        self.env = Environment(
            loader=FileSystemLoader([
                self.template_dir,  # Check in the fastapi templates directory first
                os.path.join(current_dir, 'templates')  # Fall back to base templates
            ]),
            autoescape=select_autoescape()
        )
        
        # Debug output
        if os.environ.get('DEBUG'):
            print(f"[DEBUG] Template search paths: {[self.template_dir, os.path.join(current_dir, 'templates')]}")
            print(f"[DEBUG] Template files in {self.template_dir}: {os.listdir(self.template_dir) if os.path.exists(self.template_dir) else 'Directory not found'}")

    def _generate_models(self, project_dir: str) -> str:
        """Generate SQLAlchemy models and Pydantic schemas.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            str: Path to the generated models file
        """
        # Default models if not provided in spec
        if "models" not in self.api_spec:
            self.api_spec["models"] = [
                {"name": "Item", "fields": [
                    {"name": "id", "type": "str", "required": True},
                    {"name": "name", "type": "str", "required": True},
                    {"name": "description", "type": "str", "required": False},
                    {"name": "created_at", "type": "datetime", "required": True},
                    {"name": "updated_at", "type": "datetime", "required": True}
                ]}
            ]
        
        # Transform the models data structure to match template expectations
        transformed_models = []
        for model in self.api_spec["models"]:
            transformed_model = {
                "name": model["name"],
                "fields": []
            }
            
            # Add standard fields if not already present
            standard_fields = [
                {"name": "id", "type": "str", "required": True},
                {"name": "created_at", "type": "datetime", "required": True},
                {"name": "updated_at", "type": "datetime", "required": True}
            ]
            
            # Add model-specific fields
            model_fields = model.get("fields", [])
            
            # Create a set of existing field names for quick lookup
            existing_fields = {field["name"] for field in model_fields}
            
            # Add standard fields if they don't exist
            for field in standard_fields:
                if field["name"] not in existing_fields:
                    model_fields.append(field)
            
            # Process all fields to ensure they have required attributes
            processed_fields = []
            for field in model_fields:
                if isinstance(field, str):
                    field = {"name": field, "type": "str", "required": True}
                elif isinstance(field, dict):
                    field = {
                        "name": field.get("name", ""),
                        "type": field.get("type", "str"),
                        "required": field.get("required", True),
                        "unique": field.get("unique", False),
                        "index": field.get("index", False)
                    }
                    if "default" in field:
                        field["default"] = field["default"]
                processed_fields.append(field)
            
            transformed_model["fields"] = processed_fields
            transformed_models.append(transformed_model)
        
        # Debug output
        if os.environ.get('DEBUG'):
            import pprint
            print("[DEBUG] Original API Spec models:")
            pprint.pprint(self.api_spec["models"])
            print("[DEBUG] Transformed models for template:")
            pprint.pprint(transformed_models)
            
        # Define type mappings for the template
        type_mapping = {
            'str': 'str',
            'int': 'int',
            'float': 'float',
            'bool': 'bool',
            'datetime': 'datetime',
            'date': 'date',
            'time': 'time',
            'json': 'Dict[str, Any]',
            'list': 'List[Any]',
            'url': 'HttpUrl',
            'date': 'date',
            'time': 'time',
            'json': 'Dict[str, Any]',
            'list': 'List[Any]',
            'url': 'HttpUrl',
        }
        
        db_type_mapping = {
            'str': 'String',
            'int': 'Integer',
            'float': 'Float',
            'bool': 'Boolean',
            'datetime': 'DateTime',
            'date': 'Date',
            'time': 'Time',
            'json': 'JSONB',
            'list': 'JSONB',
            'url': 'String',
        }
        
        # Render models template
        try:
            if os.environ.get('DEBUG'):
                print("[DEBUG] Rendering models template...")
                print("[DEBUG] Template path:", self.template_dir)
                print("[DEBUG] Available templates:", self.env.list_templates())
                print("[DEBUG] Models to render:")
                import pprint
                pprint.pprint(transformed_models)
            
            # Try to load the fixed template first, fall back to the original if not found
            try:
                template = self.env.get_template('models_fixed.py.j2')
                if os.environ.get('DEBUG'):
                    print("[DEBUG] Using models_fixed.py.j2 template")
            except Exception as e:
                if os.environ.get('DEBUG'):
                    print(f"[DEBUG] Could not load models_fixed.py.j2: {e}")
                template = self.env.get_template('models.py.j2')
                if os.environ.get('DEBUG'):
                    print("[DEBUG] Using models.py.j2 template")
            
            # Prepare the template context
            context = {
                'models': transformed_models,
                'TYPE_MAPPING': type_mapping,
                'DB_TYPE_MAPPING': db_type_mapping
            }
            
            # Debug the context
            if os.environ.get('DEBUG'):
                print("[DEBUG] Template context:")
                pprint.pprint(context)
            
            # Render the template
            models_content = template.render(**context)
            
            if os.environ.get('DEBUG'):
                print("[DEBUG] Rendered template content:")
                print("-" * 80)
                print(models_content)
                print("-" * 80)
                
        except Exception as e:
            if os.environ.get('DEBUG'):
                print(f"[DEBUG] Error rendering template: {e}")
                import traceback
                traceback.print_exc()
            raise
        
        # Write models file
        models_dir = os.path.join(project_dir, "app", "models")
        os.makedirs(models_dir, exist_ok=True)
        models_file = os.path.join(models_dir, "__init__.py")
        
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(models_content)
            
        return models_file

    def _generate_routers(self, project_dir: str) -> str:
        """Generate FastAPI routers for CRUD operations.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            str: Path to the generated routers directory
        """
        # Create routers directory
        routers_dir = os.path.join(project_dir, "app", "api", "v1")
        os.makedirs(routers_dir, exist_ok=True)
        
        # Create __init__.py in routers directory
        with open(os.path.join(routers_dir, "__init__.py"), 'w', encoding='utf-8') as f:
            f.write("""API v1 routers.""")
        
        # Generate router for each model
        for model in self.api_spec.get("models", []):
            template = self.env.get_template("router.py.j2")
            router_content = template.render(model=model)
            
            # Write router file
            router_file = os.path.join(routers_dir, f"{model['name'].lower()}.py")
            with open(router_file, 'w', encoding='utf-8') as f:
                f.write(router_content)
                
        return routers_dir

    def _generate_main_app(self, project_dir: str) -> str:
        """Generate the main FastAPI application file.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            str: Path to the generated main.py file
        """
        template = self.env.get_template("main.py.j2")
        main_content = template.render(
            project_name=self.project_name,
            models=self.api_spec.get("models", [])
        )
        
        # Write main.py
        main_file = os.path.join(project_dir, "app", "main.py")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_content)
            
        return main_file

    def _generate_requirements(self, project_dir: str) -> str:
        """Generate requirements.txt file.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            str: Path to the generated requirements.txt file
        """
        requirements = [
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
            "sqlalchemy>=1.4.0",
            "pydantic>=1.8.0",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "python-multipart>=0.0.5",
            "python-dotenv>=0.19.0",
            "alembic>=1.7.4",
            "psycopg2-binary>=2.9.1"
        ]
        
        requirements_file = os.path.join(project_dir, "requirements.txt")
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(requirements))
            
        return requirements_file

    def _generate_dockerfile(self, project_dir: str) -> str:
        """Generate Dockerfile for the FastAPI application.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            str: Path to the generated Dockerfile
        """
        template = self.env.get_template("Dockerfile.j2")
        dockerfile_content = template.render(
            project_name=self.project_name
        )
        
        dockerfile_path = os.path.join(project_dir, "Dockerfile")
        with open(dockerfile_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
            
        return dockerfile_path

    def _copy_static_files(self, project_dir: str) -> None:
        """Copy static files (CSS, JS, etc.) to the project directory.
        
        Args:
            project_dir: Path to the project directory
        """
        static_src = os.path.join(self.template_dir, "static")
        static_dest = os.path.join(project_dir, "app", "static")
        
        if os.path.exists(static_src):
            shutil.copytree(static_src, static_dest, dirs_exist_ok=True)

    def generate(self, **kwargs) -> str:
        """Generate FastAPI server code.
        
        Args:
            **kwargs: Additional keyword arguments
            
        Returns:
            str: Path to the generated project directory
        """
        if not self.project_name:
            raise ValueError("Project name must be set before generating FastAPI server")
            
        # Create project directory structure
        project_dir = os.path.join(self.output_dir, self.project_name)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, "app"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "app", "api"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "app", "core"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "app", "db"), exist_ok=True)
        
        # Generate project files
        self._generate_models(project_dir)
        self._generate_routers(project_dir)
        self._generate_main_app(project_dir)
        self._generate_requirements(project_dir)
        self._generate_dockerfile(project_dir)
        self._copy_static_files(project_dir)
        
        # Create empty __init__.py files
        for dirpath, _, _ in os.walk(project_dir):
            if not os.path.exists(os.path.join(dirpath, "__init__.py")):
                with open(os.path.join(dirpath, "__init__.py"), 'w', encoding='utf-8'):
                    pass
        
        return project_dir
