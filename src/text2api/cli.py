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
def generate(spec):
    """Wygeneruj API na podstawie specyfikacji tekstowej."""
    click.echo(f"Generowanie API dla: {spec}")
    generator = CLIGenerator()
    # Call the generator's generate method with the spec
    result = generator.generate(spec)
    if result:
        click.echo(result)

if __name__ == "__main__":
    main()
