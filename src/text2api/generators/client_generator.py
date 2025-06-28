"""Client generator for text2api."""
import os
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from .base_generator import BaseGenerator


class ClientGenerator(BaseGenerator):
    """Generates API client code for different programming languages."""

    def __init__(self, output_dir: str = "generated_apis"):
        """Initialize the client generator.
        
        Args:
            output_dir: Base directory where generated files will be saved
        """
        super().__init__(output_dir)
        # Store the base template directory
        self.base_template_dir = os.path.join(os.path.dirname(__file__), 'templates', 'client')
        self.env = None  # Will be initialized with the correct template dir when needed
        
    def _get_template_environment(self, language: str) -> Environment:
        """Get a Jinja2 environment for the specified language.
        
        Args:
            language: The programming language (e.g., 'python', 'typescript')
            
        Returns:
            Environment: Configured Jinja2 environment
        """
        # Set up the template directory for this language
        template_dir = os.path.join(self.base_template_dir, language)
        if not os.path.exists(template_dir):
            raise ValueError(f"Template directory not found: {template_dir}")
            
        return Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape()
        )
        
    def _generate_python_client(self, project_dir: str) -> str:
        """Generate Python client code.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            str: Path to the generated Python client file
        """
        env = self._get_template_environment("python")
        template = env.get_template("client.py.j2")
        client_content = template.render(
            project_name=self.project_name,
            models=self.api_spec.get("models", [])
        )
        
        # Create clients directory
        clients_dir = os.path.join(project_dir, "clients", "python")
        os.makedirs(clients_dir, exist_ok=True)
        
        # Write Python client file
        client_file = os.path.join(clients_dir, f"{self.project_name}_client.py")
        with open(client_file, 'w', encoding='utf-8') as f:
            f.write(client_content)
            
        # Write requirements.txt for Python client
        requirements = [
            "requests>=2.26.0",
            "pydantic>=1.8.0"
        ]
        
        requirements_file = os.path.join(clients_dir, "requirements.txt")
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(requirements))
            
        return client_file
        
    def _generate_typescript_client(self, project_dir: str) -> str:
        """Generate TypeScript client code.
        
        Args:
            project_dir: Path to the project directory
            
        Returns:
            str: Path to the generated TypeScript client file
        """
        # Create clients directory for TypeScript
        clients_dir = os.path.join(project_dir, "clients", "typescript")
        os.makedirs(clients_dir, exist_ok=True)
        
        # Get the template and render the client code
        env = self._get_template_environment("typescript")
        template = env.get_template("client.ts.j2")
        client_content = template.render(
            project_name=self.project_name,
            models=self.api_spec.get("models", [])
        )
        
        # Write TypeScript client file with .ts extension
        client_file = os.path.join(clients_dir, f"{self.project_name}Client.ts")
        with open(client_file, 'w', encoding='utf-8') as f:
            f.write(client_content)
            
        # Write package.json for TypeScript client
        package_json = {
            "name": f"{self.project_name}-client",
            "version": "1.0.0",
            "description": f"{self.project_name} API client",
            "main": "dist/index.js",
            "types": "dist/index.d.ts",
            "scripts": {
                "build": "tsc",
                "prepare": "npm run build"
            },
            "dependencies": {
                "axios": "^0.24.0"
            },
            "devDependencies": {
                "typescript": "^4.5.2",
                "@types/node": "^16.11.12"
            }
        }
        
        package_file = os.path.join(clients_dir, "package.json")
        import json
        with open(package_file, 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)
            
        # Write tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "es2018",
                "module": "commonjs",
                "declaration": True,
                "outDir": "./dist",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True
            },
            "include": ["**/*.ts"],
            "exclude": ["node_modules", "**/*.spec.ts"]
        }
        
        tsconfig_file = os.path.join(clients_dir, "tsconfig.json")
        with open(tsconfig_file, 'w', encoding='utf-8') as f:
            json.dump(tsconfig, f, indent=2)
            
        return client_file

    def generate(self, language: str = "python", **kwargs) -> str:
        """Generate API client code for the specified language.
        
        Args:
            language: Target programming language (python, typescript, etc.)
            **kwargs: Additional keyword arguments
            
        Returns:
            str: Path to the generated client file(s)
        """
        if not self.project_name:
            raise ValueError("Project name must be set before generating client code")
            
        project_dir = self.ensure_output_dir()
        
        if language.lower() == "python":
            return self._generate_python_client(project_dir)
        elif language.lower() in ["typescript", "ts"]:
            return self._generate_typescript_client(project_dir)
        else:
            raise ValueError(f"Unsupported language: {language}")
