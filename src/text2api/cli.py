import os
import click
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

from text2api.generators import (
    OpenAPIGenerator,
    FastAPIGenerator,
    ClientGenerator,
    GeneratorFactory
)
from text2api.nlp.spec_extractor import extract_spec


@click.group()
@click.version_option("0.1.6")
@click.option('--debug/--no-debug', default=False, help='Enable debug output')
@click.pass_context
def main(ctx, debug):
    """text2api - Generate servers, clients, and OpenAPI specs from text descriptions."""
    # Ensure ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug


@main.command()
def version():
    """Show the version of text2api."""
    from text2api import __version__
    click.echo(f"text2api version {__version__}")


@main.group()
@click.pass_context
def list_cmd(ctx):
    """List available generators, templates, and other resources."""
    # This is a group command that doesn't do anything on its own
    pass


def _format_output(data, output_format='text'):
    """Format output data based on the specified format.
    
    Args:
        data: Data to format
        output_format: One of 'text', 'json', or 'yaml'
        
    Returns:
        Formatted output string
    """
    if output_format == 'json':
        import json
        return json.dumps(data, indent=2)
    elif output_format == 'yaml':
        try:
            import yaml
            return yaml.dump(data, default_flow_style=False)
        except ImportError:
            click.echo("Warning: PyYAML not installed. Using JSON format instead.", err=True)
            import json
            return json.dumps(data, indent=2)
    else:  # text format
        if isinstance(data, dict):
            output = []
            for key, value in data.items():
                if isinstance(value, dict):
                    output.append(f"{key}:")
                    for k, v in value.items():
                        output.append(f"  {k}: {v}")
                else:
                    output.append(f"{key}: {value}")
            return '\n'.join(output)
        return str(data)


@list_cmd.command('generators')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['text', 'json', 'yaml'], case_sensitive=False),
              default='text', help='Output format (default: text)')
@click.pass_context
def list_generators(ctx, output_format):
    """List all available code generators."""
    from text2api.generators import GeneratorFactory
    
    generators = GeneratorFactory.get_available_generators()
    
    if output_format in ('json', 'yaml'):
        data = {
            'generators': {
                name: {
                    'description': (gen_class.__doc__ or "No description available").split('\n')[0].strip(),
                    'module': gen_class.__module__
                }
                for name, gen_class in generators.items()
            }
        }
        click.echo(_format_output(data, output_format))
    else:
        click.echo("Available generators:")
        click.echo("-" * 50)
        
        for name, gen_class in generators.items():
            doc = (gen_class.__doc__ or "No description available").split('\n')[0].strip()
            click.echo(f"{name: <10} - {doc}")
        
        click.echo("\nUse 'text2api generate <generator> --help' for more info on a specific generator.")


# Template metadata with descriptions and parameters
TEMPLATE_METADATA = {
    'fastapi': {
        'Dockerfile.j2': {
            'description': 'Dockerfile for containerizing the FastAPI application',
            'parameters': {
                'python_version': 'Python version to use in the container',
                'port': 'Port to expose in the container (default: 8000)'
            }
        },
        'main.py.j2': {
            'description': 'Main FastAPI application file with API routes and middleware',
            'parameters': {
                'app_name': 'Name of the FastAPI application',
                'version': 'API version (default: 1.0.0)'
            }
        },
        'models.py.j2': {
            'description': 'SQLAlchemy models for the database',
            'parameters': {
                'models': 'List of model definitions',
                'db_url': 'Database connection URL (default: sqlite:///./sql_app.db)'
            }
        },
        'router.py.j2': {
            'description': 'API route handlers for CRUD operations',
            'parameters': {
                'model_name': 'Name of the model this router handles',
                'prefix': 'URL prefix for the routes (default: /api/v1/)',
                'tags': 'OpenAPI tags for the routes'
            }
        }
    },
    'client': {
        'typescript/client.ts.j2': {
            'description': 'TypeScript API client with type definitions',
            'parameters': {
                'project_name': 'Name of the project',
                'models': 'List of API model definitions'
            }
        }
    },
    'openapi': {
        'openapi.yaml.j2': {
            'description': 'OpenAPI specification in YAML format',
            'parameters': {
                'title': 'API title',
                'version': 'API version (default: 1.0.0)',
                'description': 'Detailed API description'
            }
        }
    }
}

def _format_template_info(template_name, template_info, output_format='text'):
    """Format template information for display."""
    if output_format == 'text':
        output = [f"  {template_name}:"]
        output.append(f"    Description: {template_info.get('description', 'No description available')}")
        
        if 'parameters' in template_info and template_info['parameters']:
            output.append("    Parameters:")
            for param, desc in template_info['parameters'].items():
                output.append(f"      - {param}: {desc}")
        else:
            output.append("    No parameters defined.")
            
        return '\n'.join(output)
    else:
        return {
            template_name: {
                'description': template_info.get('description', ''),
                'parameters': template_info.get('parameters', {})
            }
        }

@list_cmd.command('templates')
@click.argument('generator', required=False)
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['text', 'json', 'yaml'], case_sensitive=False),
              default='text', help='Output format (default: text)')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information about each template')
@click.pass_context
def list_templates(ctx, generator, output_format, verbose):
    """List available templates for generators.
    
    If no generator is specified, lists all available templates across all generators.
    Use --verbose to see detailed information about each template.
    """
    from pathlib import Path
    
    # Get the directory where the templates are stored
    templates_dir = Path(__file__).parent / 'generators' / 'templates'
    
    if generator:
        generator = generator.lower()
        # List templates for a specific generator
        gen_templates_dir = templates_dir / generator
        if gen_templates_dir.exists() and gen_templates_dir.is_dir():
            # Get all .j2 files, including in subdirectories
            template_files = []
            for ext in ('*.j2', '*/*.j2'):
                template_files.extend(gen_templates_dir.glob(ext))
                
            templates = [str(f.relative_to(gen_templates_dir).as_posix()) 
                       for f in sorted(template_files)]
            
            if output_format in ('json', 'yaml'):
                data = {
                    'generator': generator,
                    'templates': {}
                }
                
                for tpl in templates:
                    tpl_info = TEMPLATE_METADATA.get(generator, {}).get(tpl, {})
                    data['templates'][tpl] = {
                        'description': tpl_info.get('description', 'No description available'),
                        'parameters': tpl_info.get('parameters', {})
                    }
                
                click.echo(_format_output(data, output_format))
            else:
                click.echo(f"Templates for {generator}:")
                click.echo("-" * 50)
                
                if verbose:
                    for tpl in templates:
                        tpl_info = TEMPLATE_METADATA.get(generator, {}).get(tpl, {})
                        click.echo(_format_template_info(tpl, tpl_info, 'text'))
                        click.echo()
                else:
                    for tpl in templates:
                        click.echo(f"  {tpl}")
                    click.echo("\nUse --verbose for detailed information about each template.")
        else:
            available = [d.name for d in templates_dir.iterdir() if d.is_dir()]
            if output_format in ('json', 'yaml'):
                data = {
                    'error': f"No templates found for generator: {generator}",
                    'available_generators': available
                }
                click.echo(_format_output(data, output_format), err=True)
            else:
                click.echo(f"No templates found for generator: {generator}", err=True)
                click.echo(f"Available generators with templates: {', '.join(available)}")
    else:
        # List all templates across all generators
        all_templates = {}
        for gen_dir in sorted(templates_dir.iterdir()):
            if gen_dir.is_dir():
                # Get all .j2 files, including in subdirectories
                template_files = []
                for ext in ('*.j2', '*/*.j2'):
                    template_files.extend(gen_dir.glob(ext))
                
                templates = [str(f.relative_to(gen_dir).as_posix()) 
                           for f in sorted(template_files)]
                if templates:
                    all_templates[gen_dir.name] = templates
        
        if output_format in ('json', 'yaml'):
            data = {}
            for gen_name, templates in all_templates.items():
                data[gen_name] = {}
                for tpl in templates:
                    tpl_info = TEMPLATE_METADATA.get(gen_name, {}).get(tpl, {})
                    data[gen_name][tpl] = {
                        'description': tpl_info.get('description', 'No description available'),
                        'parameters': tpl_info.get('parameters', {})
                    }
            click.echo(_format_output(data, output_format))
        else:
            click.echo("Available templates by generator:")
            click.echo("-" * 50)
            
            for gen_name, templates in all_templates.items():
                click.echo(f"\n{gen_name}:")
                if verbose:
                    for tpl in templates:
                        tpl_info = TEMPLATE_METADATA.get(gen_name, {}).get(tpl, {})
                        click.echo(_format_template_info(tpl, tpl_info, 'text'))
                        click.echo()
                else:
                    for tpl in templates:
                        click.echo(f"  {tpl}")
            
            if not verbose:
                click.echo("\nUse --verbose for detailed information about each template.")
    
    if output_format == 'text' and not verbose:
        click.echo("\nUse 'text2api list templates <generator> --verbose' to see detailed information about each template.")



@main.group()
@click.pass_context
def generate(ctx):
    """Generate API components from natural language descriptions."""
    # This is a group command that doesn't do anything on its own
    pass


def _generate_project_name(spec: str) -> str:
    """Generate a project name from the spec text."""
    # Remove special characters and limit length
    name = "".join(c if c.isalnum() else "_" for c in spec[:30].lower()).strip("_")
    return name or "api_project"


def _extract_api_spec(spec_text: str, project_name: str) -> Dict[str, Any]:
    """Extract API specification from natural language text."""
    try:
        # Use the NLP-based spec extractor
        api_spec = extract_spec(spec_text)
        
        # Ensure required fields are present
        api_spec.setdefault("name", project_name.replace("_", " ").title())
        api_spec.setdefault("description", spec_text)
        
        # Ensure models have required fields
        for model in api_spec.get("models", []):
            model.setdefault("fields", [
                {"name": "id", "type": "str", "required": True},
                {"name": "created_at", "type": "datetime", "required": True},
                {"name": "updated_at", "type": "datetime", "required": True},
            ])
        
        return api_spec
    except Exception as e:
        # Fallback to a simple spec if extraction fails
        return {
            "name": project_name.replace("_", " ").title(),
            "description": spec_text,
            "models": [
                {"name": "Item", "fields": [
                    {"name": "id", "type": "str", "required": True},
                    {"name": "name", "type": "str", "required": True},
                    {"name": "description", "type": "str", "required": False},
                    {"name": "created_at", "type": "datetime", "required": True},
                    {"name": "updated_at", "type": "datetime", "required": True},
                ]}
            ]
        }


def _prepare_generator(api_spec, project_name, generator_class, **kwargs):
    """Prepare a generator with the given API spec and project name.
    
    Args:
        api_spec: The API specification
        project_name: Name of the project
        generator_class: The generator class to instantiate
        **kwargs: Additional keyword arguments to pass to the generator
        
    Returns:
        Configured generator instance
    """
    # Filter kwargs to only include parameters that the generator accepts
    import inspect
    generator_params = inspect.signature(generator_class.__init__).parameters
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in generator_params}
    
    # Create and configure the generator with filtered kwargs
    generator = generator_class(**filtered_kwargs)
    generator.set_project_name(project_name)
    
    # Store any additional kwargs that might be needed later (e.g., for dry-run)
    generator._cli_kwargs = {k: v for k, v in kwargs.items() if k not in filtered_kwargs}
    
    # Convert the API spec to the format expected by the generator
    models = []
    endpoints = []
    
    if "models" in api_spec:
        for model in api_spec["models"]:
            fields = []
            for field in model.get("fields", []):
                fields.append({
                    "name": field.get("name", ""),
                    "type": field.get("type", "str"),
                    "required": field.get("required", False),
                    "description": field.get("description", ""),
                    "default": field.get("default", None)
                })
            models.append({
                "name": model.get("name", "Item"),
                "description": model.get("description", ""),
                "fields": fields
            })
    
    # Add some default endpoints if none are specified
    if not endpoints and "endpoints" not in api_spec:
        for model in models:
            model_name = model["name"]
            endpoints.append({
                "path": f"/{model_name.lower()}s",
                "methods": ["GET", "POST"],
                "summary": f"List and create {model_name} items",
                "model": model_name
            })
            endpoints.append({
                "path": f"/{model_name.lower()}s/{{{model_name.lower()}_id}}",
                "methods": ["GET", "PUT", "DELETE"],
                "summary": f"Retrieve, update or delete a {model_name} item",
                "model": model_name
            })
    
    # Set the API spec in the generator
    generator.set_api_spec({
        "name": api_spec.get("name", project_name),
        "description": api_spec.get("description", ""),
        "version": api_spec.get("version", "1.0.0"),
        "models": models,
        "endpoints": endpoints or api_spec.get("endpoints", [])
    })
    
    return generator


def _show_generated_files(generated_files, dry_run=False):
    """Display information about generated files.
    
    Args:
        generated_files: List of (file_path, content) tuples
        dry_run: Whether this is a dry run
    """
    if dry_run:
        click.echo("\nThe following files would be generated:")
    else:
        click.echo("\nGenerated files:")
    
    for file_path, content in generated_files:
        click.echo(f"\n{file_path}:")
        click.echo("-" * 80)
        if isinstance(content, bytes):
            try:
                click.echo(content.decode('utf-8'))
            except UnicodeDecodeError:
                click.echo("[Binary content]")
        else:
            click.echo(content)
        click.echo("-" * 80)


@generate.command()
@click.argument('spec', type=str)
@click.option('--output-dir', '-o', default='generated_apis', 
              help='Output directory for the generated files')
@click.option('--project-name', '-p', help='Project name (default: derived from spec)')
@click.option('--show-spec', is_flag=True, help='Show the extracted API specification')
@click.option('--dry-run', is_flag=True, 
              help='Preview the generated files without writing to disk')
@click.pass_context
def server(ctx, spec: str, output_dir: str, project_name: Optional[str] = None, 
          show_spec: bool = False, dry_run: bool = False):
    """Generate a FastAPI server from a text specification."""
    debug = ctx.obj.get('DEBUG', False)
    log = lambda msg: click.echo(f"DEBUG: {msg}", err=True) if debug else None
    
    click.echo(f"Generating FastAPI server for: {spec}")
    log(f"Output directory: {output_dir}")
    
    if not project_name:
        project_name = _generate_project_name(spec)
        click.echo(f"Project name: {project_name}")
    
    try:
        # Extract API spec from natural language
        click.echo("\nExtracting API specification from description...")
        api_spec = _extract_api_spec(spec, project_name)
        
        if show_spec or debug:
            click.echo("\nExtracted API Specification:")
            click.echo(json.dumps(api_spec, indent=2, ensure_ascii=False))
        
        # Create output directory if not in dry-run mode
        if not dry_run:
            os.makedirs(output_dir, exist_ok=True)
        
        # Create and configure the generator
        click.echo("\nGenerating FastAPI server code...")
        generator = _prepare_generator(
            api_spec, 
            project_name,
            FastAPIGenerator,
            output_dir=output_dir
        )
        
        # Generate the server
        if dry_run:
            # In dry-run mode, collect the files that would be generated
            generated_files = []
            
            # Simulate file generation by collecting the content
            # This is a simplified example - actual implementation would depend on the generator
            project_dir = os.path.join(output_dir, project_name)
            
            # Simulate models file
            models_content = "# Simulated models.py\n# This is a preview of what would be generated\n"
            models_content += f"# Project: {project_name}\n"
            models_content += "# Models:\n"
            for model in api_spec.get("models", []):
                models_content += f"# - {model.get('name', 'Unknown')}\n"
            
            generated_files.append((
                os.path.join(project_dir, "app", "models", "__init__.py"),
                models_content
            ))
            
            # Simulate main.py
            main_content = "# Simulated main.py\nfrom fastapi import FastAPI\n\n"
            main_content += f'app = FastAPI(title="{project_name}")\n\n'
            main_content += "@app.get(\"/\")\n"
            main_content += "def read_root():\n"
            main_content += "    return {\"message\": \"Hello, World!\"}"
            
            generated_files.append((
                os.path.join(project_dir, "app", "main.py"),
                main_content
            ))
            
            # Show the preview
            _show_generated_files(generated_files, dry_run=True)
            
            click.echo("\n✅ This was a dry run. No files were written to disk.")
            click.echo("Remove the --dry-run flag to generate the actual files.")
        else:
            # Actual generation
            result = generator.generate()
            click.echo(f"\n✅ Successfully generated FastAPI server at: {result}")
            
            # Show next steps
            click.echo("\nNext steps:")
            click.echo(f"1. cd {result}")
            click.echo("2. pip install -r requirements.txt")
            click.echo("3. uvicorn app.main:app --reload")
            click.echo("\nOpen http://localhost:8000/docs to view the API documentation")
        
    except Exception as e:
        click.echo(f"\n❌ Error generating server: {str(e)}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


# Backward compatibility with the old command structure
@main.command()
@click.argument('spec', type=str)
@click.option('--output-dir', '-o', default='generated_apis', 
              help='Output directory for the generated files')
@click.option('--project-name', '-p', help='Project name (default: derived from spec)')
@click.option('--show-spec', is_flag=True, help='Show the extracted API specification')
@click.pass_context
def generate_legacy(ctx, spec: str, output_dir: str, project_name: Optional[str] = None, show_spec: bool = False):
    """Legacy command for backward compatibility. Generates a complete API project."""
    click.echo("⚠️  Note: The 'generate' command is deprecated. Use 'generate server' instead.")
    ctx.invoke(server, spec=spec, output_dir=output_dir, project_name=project_name, show_spec=show_spec)


@generate.command()
@click.argument('spec', type=str)
@click.option('--output-dir', '-o', default='generated_apis', 
              help='Output directory for the generated files')
@click.option('--language', '-l', default='python', 
              type=click.Choice(['python', 'typescript', 'javascript'], case_sensitive=False),
              help='Programming language for the client (default: python)')
@click.option('--project-name', '-p', help='Project name (default: derived from spec)')
@click.option('--show-spec', is_flag=True, help='Show the extracted API specification')
@click.option('--dry-run', is_flag=True, 
              help='Preview the generated files without writing to disk')
@click.pass_context
def client(ctx, spec: str, output_dir: str, language: str, project_name: Optional[str] = None, 
          show_spec: bool = False, dry_run: bool = False):
    """Generate an API client from a text specification."""
    debug = ctx.obj.get('DEBUG', False)
    log = lambda msg: click.echo(f"DEBUG: {msg}", err=True) if debug else None
    
    click.echo(f"Generating {language} client for: {spec}")
    log(f"Output directory: {output_dir}")
    
    if not project_name:
        project_name = _generate_project_name(spec)
        click.echo(f"Project name: {project_name}")
    
    try:
        # Extract API spec from natural language
        click.echo("\nExtracting API specification from description...")
        api_spec = _extract_api_spec(spec, project_name)
        
        if show_spec or debug:
            click.echo("\nExtracted API Specification:")
            click.echo(json.dumps(api_spec, indent=2, ensure_ascii=False))
        
        # Create output directory if not in dry-run mode
        if not dry_run:
            os.makedirs(output_dir, exist_ok=True)
        
        # Create and configure the generator
        click.echo(f"\nGenerating {language} client code...")
        generator = _prepare_generator(
            api_spec, 
            project_name,
            ClientGenerator,
            output_dir=output_dir,
            language=language  # This will be filtered by _prepare_generator
        )
        
        # Generate the client
        if dry_run:
            # In dry-run mode, collect the files that would be generated
            generated_files = []
            project_dir = os.path.join(output_dir, project_name)
            
            # Simulate client file
            client_content = f"# Simulated {language} client\n"
            client_content += f"# Project: {project_name}\n"
            client_content += "# This is a preview of what would be generated\n\n"
            
            # Add some example API methods based on the spec
            if "endpoints" in api_spec:
                for endpoint in api_spec["endpoints"][:3]:  # Show first 3 endpoints
                    path = endpoint.get("path", "")
                    methods = endpoint.get("methods", [])
                    if methods:
                        method = methods[0].lower()
                        client_content += f"def {method}_{path.replace('/', '_').strip('_')}():"
                        client_content += f"  # {endpoint.get('summary', '')}\n"
                        client_content += "  pass\n\n"
            
            generated_files.append((
                os.path.join(project_dir, f"client.{'py' if language == 'python' else 'ts'}"),
                client_content
            ))
            
            # Add a README if it's a TypeScript/JavaScript client
            if language in ['typescript', 'javascript']:
                readme_content = f"# {project_name} Client\n\n"
                readme_content += f"This is a {language} client generated by text2api.\n\n"
                readme_content += "## Installation\n\n```bash\nnpm install\n```\n\n"
                readme_content += "## Usage\n\n```typescript\nimport {{ Client }} from './client';\n\nconst client = new Client();\n// Use client methods here\n```"
                
                generated_files.append((
                    os.path.join(project_dir, "README.md"),
                    readme_content
                ))
            
            # Show the preview
            _show_generated_files(generated_files, dry_run=True)
            
            click.echo("\n✅ This was a dry run. No files were written to disk.")
            click.echo("Remove the --dry-run flag to generate the actual files.")
        else:
            # Actual generation
            result = generator.generate(language=language)
            click.echo(f"\n✅ Successfully generated {language} client at: {result}")
            
            # Show next steps
            click.echo("\nNext steps:")
            click.echo(f"1. cd {result}")
            if language == 'python':
                click.echo("2. pip install -r requirements.txt")
                click.echo("3. Import and use the client in your code")
            else:
                click.echo("2. npm install")
                click.echo("3. Import and use the client in your code")
        
    except Exception as e:
        click.echo(f"\n❌ Error generating {language} client: {str(e)}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@generate.command()
@click.argument('spec', type=str)
@click.option('--output-dir', '-o', default='generated_apis', 
              help='Output directory for the generated files')
@click.option('--project-name', '-p', help='Project name (default: derived from spec)')
@click.option('--show-spec', is_flag=True, help='Show the extracted API specification')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['yaml', 'json'], case_sensitive=False),
              default='yaml', help='Output format (default: yaml)')
@click.option('--dry-run', is_flag=True, 
              help='Preview the generated OpenAPI spec without writing to disk')
@click.pass_context
def openapi(ctx, spec: str, output_dir: str, project_name: Optional[str] = None, 
          show_spec: bool = False, output_format: str = 'yaml', dry_run: bool = False):
    """Generate an OpenAPI specification from a text description."""
    debug = ctx.obj.get('DEBUG', False)
    log = lambda msg: click.echo(f"DEBUG: {msg}", err=True) if debug else None
    
    click.echo(f"Generating OpenAPI spec for: {spec}")
    log(f"Output directory: {output_dir}")
    log(f"Output format: {output_format}")
    
    if not project_name:
        project_name = _generate_project_name(spec)
        click.echo(f"Project name: {project_name}")
    
    try:
        # Extract API spec from natural language
        click.echo("\nExtracting API specification from description...")
        api_spec = _extract_api_spec(spec, project_name)
        
        if show_spec or debug:
            click.echo("\nExtracted API Specification:")
            click.echo(json.dumps(api_spec, indent=2, ensure_ascii=False))
        
        # Create output directory if not in dry-run mode
        if not dry_run:
            os.makedirs(output_dir, exist_ok=True)
        
        # Create and configure the generator
        click.echo("\nGenerating OpenAPI specification...")
        generator = _prepare_generator(
            api_spec, 
            project_name,
            OpenAPIGenerator,
            output_dir=output_dir
        )
        
        if dry_run:
            # In dry-run mode, show what would be generated
            output_file = os.path.join(output_dir, project_name, f"openapi_spec.{output_format}")
            
            # Create a sample OpenAPI spec based on the extracted API spec
            sample_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": api_spec.get("name", project_name),
                    "description": api_spec.get("description", ""),
                    "version": api_spec.get("version", "1.0.0")
                },
                "paths": {},
                "components": {
                    "schemas": {}
                }
            }
            
            # Add sample paths and schemas based on the API spec
            if "endpoints" in api_spec:
                for endpoint in api_spec["endpoints"][:3]:  # Show first 3 endpoints
                    path = endpoint.get("path", "")
                    methods = endpoint.get("methods", [])
                    
                    if path and methods:
                        sample_spec["paths"][path] = {}
                        for method in methods[:2]:  # Show first 2 methods per endpoint
                            sample_spec["paths"][path][method.lower()] = {
                                "summary": endpoint.get("summary", ""),
                                "responses": {
                                    "200": {
                                        "description": "Successful response"
                                    }
                                }
                            }
            
            # Format the output
            if output_format == 'json':
                import json
                content = json.dumps(sample_spec, indent=2)
            else:  # yaml
                try:
                    import yaml
                    content = yaml.dump(sample_spec, default_flow_style=False)
                except ImportError:
                    # Fall back to JSON if PyYAML is not available
                    import json
                    content = json.dumps(sample_spec, indent=2)
            
            # Show the preview
            _show_generated_files([(output_file, content)], dry_run=True)
            
            click.echo("\n✅ This was a dry run. No files were written to disk.")
            click.echo("Remove the --dry-run flag to generate the actual OpenAPI spec.")
        else:
            # Actual generation
            result = generator.generate(format=output_format)
            click.echo(f"\n✅ Successfully generated OpenAPI spec at: {result}")
            
            # Show next steps
            click.echo("\nNext steps:")
            click.echo(f"1. Inspect the generated OpenAPI spec: {result}")
            click.echo("2. Use with tools like Swagger UI, Redoc, or API gateways")
        
    except Exception as e:
        click.echo(f"\n❌ Error generating OpenAPI spec: {str(e)}", err=True)
        if debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def main_wrapper():
    """Wrapper for the main function to ensure proper error handling."""
    try:
        main(obj={})
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main_wrapper()
