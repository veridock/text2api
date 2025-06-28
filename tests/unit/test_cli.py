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

@pytest.mark.parametrize(
    "command, expected_output",
    [
        ("test", "Generowanie API dla: test"),
    ],
)
def test_generate_command(command, expected_output, mocker):
    """Test the generate command with different inputs."""
    # Create a mock for the CLIGenerator class
    mock_generator = mocker.MagicMock()
    # Make the generate method return a specific value
    mock_generator.generate.return_value = f"Successfully generated CLI for: {command}"
    # Patch the CLIGenerator class to return our mock instance
    mocker.patch('text2api.generators.cli_gen.CLIGenerator', return_value=mock_generator)
    
    # Run the CLI command
    runner = CliRunner()
    result = runner.invoke(cli_main, ["generate", command])
    
    # Verify the results
    assert result.exit_code == 0
    assert expected_output.lower() in result.output.lower()
    # Verify the generate method was called with the correct argument
    mock_generator.generate.assert_called_once_with(command)
