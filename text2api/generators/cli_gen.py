"""
Generator dla CLI tools
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from text2api.core.file_manager import FileManager
from text2api.models import ApiSpec


class CLIGenerator:
    """Generator CLI tools używając Click"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Ładuje szablony Jinja2 dla CLI"""
        templates_dir = Path(__file__).parent / 'templates' / 'cli'
        
        # Ensure templates directory exists
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default templates if they don't exist
        default_templates = {
            'cli.py.j2': '''#!/usr/bin/env python3
"""
{{ api_spec.name }} CLI

{{ api_spec.description }}
CLI tool generated by text2api
"""

import click
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

__version__ = "0.1.0"

class {{ api_spec.name|title }}CLI:
    """{{ api_spec.description }}"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".{{ api_spec.name|lower }}"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config()
        self.logger = self._get_logger()
    
    def _ensure_config(self) -> None:
        """Ensure config directory and file exist"""
        self.config_dir.mkdir(exist_ok=True, parents=True)
        if not self.config_file.exists():
            self.config_file.write_text('{"version": "' + __version__ + '"}')

    def _get_logger(self):
        """Get configured logger"""
        logger = logging.getLogger("{{ api_spec.name|title }}CLI")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

cli = {{ api_spec.name|title }}CLI()

@click.group()
@click.version_option(__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
CLI tool generated by text2api
"""

import click
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

__version__ = "0.1.0"

class {{ api_spec.name|title }}CLI:
    """{{ api_spec.description }}"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".{{ api_spec.name|lower }}"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config()
        self.logger = self._get_logger()
    
    def _ensure_config(self) -> None:
        """Ensure config directory and file exist"""
        self.config_dir.mkdir(exist_ok=True, parents=True)
        if not self.config_file.exists():
            self.config_file.write_text('{"version": "' + __version__ + '"}')

    def _get_logger(self):
        """Get configured logger"""
        logger = logging.getLogger("{{ api_spec.name|title }}CLI")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

cli = {{ api_spec.name|title }}CLI()

@click.group()
@click.version_option(__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def main(ctx, verbose):
    """{{ api_spec.name }} CLI"""
    if verbose:
        cli.logger.setLevel(logging.DEBUG)
        cli.logger.debug("Verbose mode enabled")
    ctx.obj = cli

@main.command()
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.pass_obj
def status(cli, format):
    """Show system status"""
    status_data = {
        'version': __version__,
        'config_file': str(cli.config_file),
        'status': 'running'
    }
    click.echo(json.dumps(status_data, indent=2) if format == 'json' else "\n".join(f"{k}: {v}" for k, v in status_data.items()))

{% if api_spec.database_required %}
@main.group()
@click.pass_obj
def db(cli):
    """Database management commands"""
    pass

@db.command()
@click.pass_obj
def init(cli):
    """Initialize database"""
    click.echo("Database initialized")

@db.command()
@click.argument('backup_file', type=click.Path())
@click.pass_obj
def backup(cli, backup_file):
    """Backup database"""
    click.echo(f"Database backed up to {backup_file}")

@db.command()
@click.argument('backup_file', type=click.Path(exists=True))
@click.pass_obj
def restore(cli, backup_file):
    """Restore database from backup"""
    click.echo(f"Database restored from {backup_file}")
{% endif %}

{% for model in api_spec.models %}
@main.group()
@click.pass_obj
def {{ model.name|lower }}(cli):
    """{{ model.name }} management commands"""
    pass

@{{ model.name|lower }}.command('list')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.pass_obj
def list_{{ model.name|lower }}s(cli, format):
    """List all {{ model.name }}s"""
    items = []  # Replace with actual data
    click.echo(json.dumps(items, indent=2) if format == 'json' else "\n".join(str(item) for item in items))

@{{ model.name|lower }}.command('get')
@click.argument('id')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
@click.pass_obj
def get_{{ model.name|lower }}(cli, id, format):
    """Get {{ model.name }} by ID"""
    item = None  # Replace with actual data
    click.echo(json.dumps(item, indent=2) if format == 'json' and item else f"{{ model.name }} {id} not found")

@{{ model.name|lower }}.command('create')
@click.option('--data', type=click.Path(exists=True))
@click.pass_obj
def create_{{ model.name|lower }}(cli, data):
    """Create a new {{ model.name }}"""
    click.echo(f"Created new {{ model.name|lower }}")

@{{ model.name|lower }}.command('update')
@click.argument('id')
@click.option('--data', type=click.Path(exists=True))
@click.pass_obj
def update_{{ model.name|lower }}(cli, id, data):
    """Update a {{ model.name }}"""
    click.echo(f"Updated {{ model.name|lower }} {id}")

@{{ model.name|lower }}.command('delete')
@click.argument('id')
@click.option('--force', is_flag=True)
@click.pass_obj
def delete_{{ model.name|lower }}(cli, id, force):
    """Delete a {{ model.name }}"""
    click.echo(f"Deleted {{ model.name|lower }} {id}")
{% endfor %}

if __name__ == '__main__':
    main()
'''
        }
cli = {{ api_spec.name|title }}CLI()

# CLI Commands
@click.group()
@click.version_option(__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def main(ctx, verbose):
    # {{ api_spec.name }} CLI
    if verbose:
        cli.logger.setLevel(logging.DEBUG)
        cli.logger.debug("Verbose mode enabled")
    
    ctx.obj = cli

@main.command()
@click.option('--format', type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='Output format')
@click.pass_obj
def status(cli, format):
    # Display system status
    status_data = {
        'version': __version__,
        'config_file': str(cli.config_file),
        'log_file': str(cli.log_file),
        'status': 'running'
    }
    
    if format == 'json':
        cli._print_json(status_data)
    elif format == 'csv':
        cli._print_csv([status_data])
    else:
        click.echo("=== System Status ===")
        for key, value in status_data.items():
            click.echo(f"{key}: {value}")

{% if api_spec.database_required %}
@main.group()
@click.pass_obj
def db(cli):
    # Database management commands
    pass

@db.command()
@click.pass_obj
def init(cli):
    # Initialize database
    try:
        # Add database initialization code here
        cli.logger.info("Database initialized")
        click.echo("Database initialized successfully")
    except Exception as e:
        cli.logger.error(f"Error initializing database: {e}")
        raise click.ClickException(f"Failed to initialize database: {e}")

@db.command()
@click.argument('backup_file', type=click.Path())
@click.pass_obj
def backup(cli, backup_file):
    # Backup database
    try:
        # Add database backup code here
        cli.logger.info(f"Database backed up to {backup_file}")
        click.echo(f"Database backed up to {backup_file}")
    except Exception as e:
        cli.logger.error(f"Error backing up database: {e}")
        raise click.ClickException(f"Failed to backup database: {e}")

@db.command()
@click.argument('backup_file', type=click.Path(exists=True))
@click.pass_obj
def restore(cli, backup_file):
    # Restore database from backup
    try:
        # Add database restore code here
        cli.logger.info(f"Database restored from {backup_file}")
        click.echo(f"Database restored from {backup_file}")
    except Exception as e:
        cli.logger.error(f"Error restoring database: {e}")
        raise click.ClickException(f"Failed to restore database: {e}")
{% endif %}

{% for model in api_spec.models %}
@main.group()
@click.pass_obj
def {{ model.name|lower }}(cli):
    # {{ model.name }} management commands
    pass

@{{ model.name|lower }}.command('list')
@click.option('--format', type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file')
@click.pass_obj
def list_{{ model.name|lower }}s(cli, format, output):
    # List all {{ model.name }}s
    try:
        # Add code to fetch {{ model.name }}s here
        items = []  # Replace with actual data
        
        if format == 'json':
            if output:
                with open(output, 'w') as f:
                    json.dump(items, f, indent=2)
                click.echo(f"Data exported to {output}")
            else:
                cli._print_json(items)
        elif format == 'csv':
            cli._print_csv(items, output)
        else:
            if items:
                cli._print_table(items)
            else:
                click.echo("No {{ model.name }}s found")
    except Exception as e:
        cli.logger.error(f"Error listing {{ model.name|lower }}s: {e}")
        raise click.ClickException(f"Failed to list {{ model.name|lower }}s: {e}")

@{{ model.name|lower }}.command('get')
@click.argument('id', type=str)
@click.option('--format', type=click.Choice(['table', 'json']), 
              default='table', help='Output format')
@click.pass_obj
def get_{{ model.name|lower }}(cli, id, format):
    """Get {{ model.name }} by ID"""
    try:
        # Add code to fetch {{ model.name }} by ID here
        item = None  # Replace with actual data
        
        if not item:
            click.echo(f"{{ model.name }} with ID {id} not found")
            return
            
        if format == 'json':
            cli._print_json(item)
        else:
            click.echo(f"=== {{ model.name }}: {id} ===")
            for key, value in item.items():
                click.echo(f"{key}: {value}")
    except Exception as e:
        cli.logger.error(f"Error getting {{ model.name|lower }} {id}: {e}")
        raise click.ClickException(f"Failed to get {{ model.name|lower }}: {e}")

@{{ model.name|lower }}.command('create')
@click.option('--data', '-d', type=click.Path(exists=True), 
              help='Path to JSON file with data')
@click.option('--format', type=click.Choice(['table', 'json']), 
              default='table', help='Output format')
@click.pass_context
def create_{{ model.name|lower }}(ctx, data, format):
    # Create a new {{ model.name }}
    cli = ctx.obj
    
    try:
        if data:
            # Load data from file
            with open(data) as f:
                item_data = json.load(f)
        else:
            # Interactive mode - prompt for data
            item_data = {}
            {% for field in model.fields %}
            item_data['{{ field.name }}'] = click.prompt('{{ field.name }}', 
                type={{ 'int' if field.type == 'integer' else 'str' }}, 
                default='' if not field.required else None)
            {% endfor %}
        
        # Add code to create {{ model.name }} here
        created_item = item_data  # Replace with actual created item
        
        if format == 'json':
            cli._print_json(created_item)
        else:
            click.echo(f"{{ model.name }} created successfully")
            for key, value in created_item.items():
                click.echo(f"{key}: {value}")
    except Exception as e:
        cli.logger.error(f"Error creating {{ model.name|lower }}: {e}")
        raise click.ClickException(f"Failed to create {{ model.name|lower }}: {e}")

@{{ model.name|lower }}.command('update')
@click.argument('id', type=str)
@click.option('--data', '-d', type=click.Path(exists=True), 
              help='Path to JSON file with data')
@click.option('--format', type=click.Choice(['table', 'json']), 
              default='table', help='Output format')
@click.pass_obj
def update_{{ model.name|lower }}(cli, id, data, format):
    # Update a {{ model.name }}
    try:
        if data:
            # Load data from file
            with open(data) as f:
                update_data = json.load(f)
        else:
            # Interactive mode - prompt for data
            update_data = {}
            {% for field in model.fields %}
            if click.confirm(f'Update {{ field.name }}?'):
                update_data['{{ field.name }}'] = click.prompt('{{ field.name }}', 
                    type={{ 'int' if field.type == 'integer' else 'str' }})
            {% endfor %}
        
        # Add code to update {{ model.name }} here
        updated_item = update_data  # Replace with actual updated item
        
        if format == 'json':
            cli._print_json(updated_item)
        else:
            click.echo(f"{{ model.name }} {id} updated successfully")
    except Exception as e:
        cli.logger.error(f"Error updating {{ model.name|lower }} {id}: {e}")
        raise click.ClickException(f"Failed to update {{ model.name|lower }}: {e}")

@{{ model.name|lower }}.command('delete')
@click.argument('id', type=str)
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
@click.pass_obj
def delete_{{ model.name|lower }}(cli, id, force):
    # Delete a {{ model.name }}
    try:
        if not force and not click.confirm(f'Are you sure you want to delete {{ model.name|lower }} {id}?'):
            click.echo('Operation cancelled')
            return
        
        # Add code to delete {{ model.name }} here
        
        click.echo(f"{{ model.name }} {id} deleted successfully")
    except Exception as e:
        cli.logger.error(f"Error deleting {{ model.name|lower }} {id}: {e}")
        raise click.ClickException(f"Failed to delete {{ model.name|lower }}: {e}")

@{{ model.name|lower }}.command('import')
@click.argument('file', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['json', 'csv']), 
              default='json', help='Input format')
@click.option('--batch-size', type=int, default=100, 
              help='Number of records to process in each batch')
@click.pass_obj
def import_{{ model.name|lower }}s(cli, file, format, batch_size):
    # Import {{ model.name }}s from file
    try:
        if format == 'json':
            with open(file) as f:
                items = json.load(f)
        else:  # CSV
            with open(file, newline='') as f:
                reader = csv.DictReader(f)
                items = list(reader)
        
        # Process items in batches
        total = len(items)
        click.echo(f"Importing {total} {{ model.name|lower }}(s)...")
        
        for i in range(0, total, batch_size):
            batch = items[i:i + batch_size]
            # Add code to process batch here
            click.echo(f"Processed batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size}")
        
        click.echo(f"Successfully imported {total} {{ model.name|lower }}(s)")
    except Exception as e:
        cli.logger.error(f"Error importing {{ model.name|lower }}s: {e}")
        raise click.ClickException(f"Failed to import {{ model.name|lower }}s: {e}")

@{{ model.name|lower }}.command('export')
@click.argument('output', type=click.Path())
@click.option('--format', type=click.Choice(['json', 'csv']), 
              default='json', help='Output format')
@click.pass_obj
def export_{{ model.name|lower }}s(cli, output, format):
    # Export {{ model.name }}s to file
    try:
        # Add code to fetch all {{ model.name }}s here
        items = []  # Replace with actual data
        
        if format == 'json':
            with open(output, 'w') as f:
                json.dump(items, f, indent=2)
        else:  # CSV
            if not items:
                click.echo("No data to export")
                return
                
            fieldnames = list(items[0].keys())
            with open(output, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(items)
        
        click.echo(f"Exported {len(items)} {{ model.name|lower }}(s) to {output}")
    except Exception as e:
        cli.logger.error(f"Error exporting {{ model.name|lower }}s: {e}")
        raise click.ClickException(f"Failed to export {{ model.name|lower }}s: {e}")

{% endfor %}

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    main()
"""

        requirements_txt = """click>=8.0.0
tabulate>=0.8.9
{% if api_spec.database_required %}
sqlite3>=2.6.0
{% endif %}
"""

        readme_md = """# {{ api_spec.name }} CLI

This is an auto-generated CLI tool for {{ api_spec.name }}.

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make the script executable:
   ```bash
   chmod +x cli.py
   ```

## Usage

```
./cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help     Show this message and exit.
  --version  Show the version and exit.
  -v, --verbose  Enable verbose output

Commands:
  db      Database management commands
  status  Show system status
  {% for model in api_spec.models %}
  {{ "%-8s"|format(model.name|lower) }}  {{ model.name }} management commands
  {% endfor %}
```

## Examples

Show system status:
```
./cli.py status
```

List all items:
```
./cli.py {{ api_spec.models[0].name|lower }} list
```

Create a new item (interactive):
```
./cli.py {{ api_spec.models[0].name|lower }} create
```

Import data from a file:
```
./cli.py {{ api_spec.models[0].name|lower }} import data.json
```
"""
}

        return {
            'cli.py': cli_template,
            'requirements.txt': requirements_txt,
            'README.md': readme_md
        }

    async def generate(self, api_spec: ApiSpec, output_path: Path) -> Dict[str, str]:
        """
        Generuje kod CLI na podstawie specyfikacji API
        
        Args:
            api_spec: Specyfikacja API
            output_path: Ścieżka do katalogu wyjściowego
            
        Returns:
            Słownik zawierający wygenerowane pliki
        """
        generated_files = {}  # Initialize empty dictionary for generated files
        env = Environment()
        
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate cli.py
        cli_template = env.from_string(self.templates['cli.py'])
        cli_content = cli_template.render(api_spec=api_spec)
        
        cli_file = output_path / 'cli.py'
        await self.file_manager.write_file(cli_file, cli_content)
        generated_files['cli.py'] = str(cli_file)
        
        # Make cli.py executable
        cli_file.chmod(0o755)
        
        # Generate requirements.txt
        requirements_template = env.from_string(self.templates['requirements.txt'])
        requirements_content = requirements_template.render(api_spec=api_spec)
        
        requirements_file = output_path / 'requirements.txt'
        await self.file_manager.write_file(requirements_file, requirements_content)
        generated_files['requirements.txt'] = str(requirements_file)
        
        # Generate README.md
        readme_template = env.from_string(self.templates['README.md'])
        readme_content = readme_template.render(api_spec=api_spec)
        
        readme_file = output_path / 'README.md'
        await self.file_manager.write_file(readme_file, readme_content)
        generated_files['README.md'] = str(readme_file)
        
        return generated_files
