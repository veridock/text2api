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

@main.command()
@click.argument('spec', type=str)
@click.option('--debug', is_flag=True, help='Enable debug output')
def generate(spec, debug):
    """Wygeneruj API na podstawie specyfikacji tekstowej."""
    if debug:
        click.echo("DEBUG: Starting generate command", err=True)
        click.echo(f"DEBUG: spec = {spec!r}", err=True)
    
    click.echo(f"Generowanie API dla: {spec}")
    
    if debug:
        click.echo("DEBUG: Creating CLIGenerator instance", err=True)
    generator = CLIGenerator()
    
    if debug:
        click.echo("DEBUG: Calling generator.generate()", err=True)
    # Call the generator's generate method with the spec
    result = generator.generate(spec)
    
    if debug:
        click.echo(f"DEBUG: generator.generate() returned: {result!r}", err=True)
    
    if result:
        click.echo(result)

if __name__ == "__main__":
    main()
