"""Unit tests for the text2api CLI."""

import pytest
from click.testing import CliRunner
from text2api.cli import main as cli_main

def test_cli_help():
    """Test the CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli_main, ['--help'])
    assert result.exit_code == 0
    assert 'Show this message and exit.' in result.output

def test_cli_version():
    """Test the CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli_main, ['--version'])
    assert result.exit_code == 0
    assert 'version' in result.output.lower()

@pytest.mark.parametrize("command,expected_output", [
    (['generate', 'test'], 'Generating API for: test'),
])
def test_generate_command(command, expected_output):
    """Test the generate command with different inputs."""
    runner = CliRunner()
    result = runner.invoke(cli_main, command)
    assert result.exit_code == 0
    assert expected_output.lower() in result.output.lower()
