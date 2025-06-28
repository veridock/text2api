"""Unit tests for the text2api CLI."""

import pytest
import sys
from unittest import mock
from click.testing import CliRunner
from text2api import cli as cli_module

# Alias for the main function to test
cli_main = cli_module.main

def test_cli_help():
    """Test the CLI help output."""
    runner = CliRunner()
    result = runner.invoke(cli_main, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.output
    assert "generate" in result.output  # Make sure subcommands are listed
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
    mock_generator.generate.return_value = f"Successfully generated CLI for: {command}"
    
    # Patch the CLIGenerator class where it's used in the cli module
    with mocker.patch('text2api.cli.CLIGenerator', return_value=mock_generator) as mock_cls:
        # Run the CLI command with debug flag
        runner = CliRunner()
        result = runner.invoke(cli_main, ["generate", command, "--debug"])
        
        # Verify the results
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert expected_output.lower() in result.output.lower(), \
            f"Expected '{expected_output}' in output, got: {result.output}"
        
        # Verify the generate method was called with the correct argument
        mock_generator.generate.assert_called_once_with(command)
