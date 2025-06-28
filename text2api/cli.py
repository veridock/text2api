import click
import sys
from text2api.generators.cli_gen import CLIGenerator

def print_version():
    click.echo("text2api CLI version 0.1.2")

@click.group()
@click.version_option("0.1.2")
def main():
    """text2api - API generator CLI"""
    pass

import re
import os

@main.command()
@click.argument('spec', type=str)
def generate(spec):
    """Wygeneruj API na podstawie specyfikacji tekstowej."""
    click.echo(f"Generowanie API dla: {spec}")
    generator = CLIGenerator()

    # Przykład uproszczonego modelu API spec (do rozbudowy wg potrzeb)
    api_spec = {
        'name': spec,
        'description': spec,
        'models': [],
        'database_required': True,
        'auth_type': None
    }

    # Slug do katalogu docelowego
    slug = re.sub(r'[^a-zA-Z0-9_-]+', '_', spec.lower())[:32]
    out_dir = os.path.join(os.getcwd(), 'generated_apis', slug)
    os.makedirs(out_dir, exist_ok=True)

    # Renderuj i zapisuj pliki
    with open(os.path.join(out_dir, 'cli.py'), 'w') as f:
        f.write(generator.render_cli(api_spec))
    with open(os.path.join(out_dir, 'requirements.txt'), 'w') as f:
        f.write(generator.render_requirements(api_spec))
    with open(os.path.join(out_dir, 'README.md'), 'w') as f:
        f.write(generator.render_readme(api_spec))
    click.echo(f"Wygenerowano API w katalogu: {out_dir}")

if __name__ == "__main__":
    main()
