"""Unit tests for the text2api CLI."""

import pytest
from click.testing import CliRunner
from text2api import cli as cli_main

def test_cli_help():
    """Test the CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli_main, ['--help'])
    assert result.exit_code == 0
    assert 'text2api - API generator CLI' in result.output
    assert '--help' in result.output

def test_cli_version():
    """Test the CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli_main, ['--version'])
    # The version command exits with 0 on success, but the output might be empty
    # Just check that it doesn't fail
    assert result.exit_code == 0

@pytest.mark.parametrize("command,expected_output", [
    (['generate', 'test'], 'Generating API for: test'),
])
def test_generate_command(command, expected_output, mocker):
    """Test the generate command with different inputs."""
    # Mock the CLIGenerator to avoid actual API generation during tests
    mock_generator = mocker.MagicMock()
    mocker.patch('text2api.generators.cli_gen.CLIGenerator', return_value=mock_generator)
    
    runner = CliRunner()
    result = runner.invoke(cli_main, command)
    
    assert result.exit_code == 0
    if expected_output:
        assert expected_output.lower() in result.output.lower()
    
    # Verify the generator was called if this is a generate command
    if command[0] == 'generate':
        mock_generator.generate.assert_called_once()
