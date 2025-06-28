"""Unit tests for the text2api CLI."""

from unittest import mock  # noqa: F401

from click.testing import CliRunner

from text2api.cli import main as cli_main


def test_cli_help():
    """Test the CLI help output."""
    runner = CliRunner()
    result = runner.invoke(cli_main, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit." in result.output
    assert "generate" in result.output


def test_cli_version():
    """Test the CLI version output."""
    runner = CliRunner()
    result = runner.invoke(cli_main, ["--version"])
    assert result.exit_code == 0
    assert "version 0.1.2" in result.output


def test_generate_command_basic(mocker):
    """Test the generate command with a basic input."""
    mock_generator = mocker.MagicMock()
    mock_generator.generate.return_value = "Test output"

    # Patch the CLIGenerator class
    with mocker.patch('text2api.cli.CLIGenerator', return_value=mock_generator):
        runner = CliRunner()
        result = runner.invoke(cli_main, ["generate", "test_spec"])
        
        assert result.exit_code == 0
        assert "Test output" in result.output
        mock_generator.generate.assert_called_once_with("test_spec")


def test_generate_command_with_debug(mocker, monkeypatch):
    """Test the generate command with debug output."""
    # Create a mock for the CLIGenerator class
    mock_generator = mocker.MagicMock()
    mock_generator.generate.return_value = "Test output"
    
    echo_calls = []

    def mock_echo(message, **kwargs):
        echo_calls.append((message, kwargs.get('err', False)))

    # Patch the CLIGenerator class and the click.echo function
    with mocker.patch('text2api.cli.CLIGenerator', 
                     return_value=mock_generator):
        # Replace click.echo with our mock
        monkeypatch.setattr('click.echo', mock_echo)
        
        # Run the CLI command with debug flag
        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            ["generate", "test_spec", "--debug"]
        )

        # Check the command executed successfully
        assert result.exit_code == 0
        
        # Convert the echo calls to a set of (message, is_error) tuples
        echo_messages = set()
        for call in echo_calls:
            if len(call) == 2 and isinstance(call, tuple):
                message, is_error = call
                echo_messages.add((message, is_error))

        # Check that debug messages were printed (order independent)
        expected_messages = {
            ("DEBUG: Starting generate command", True),
            ("DEBUG: spec = 'test_spec'", True),
            ("DEBUG: Creating CLIGenerator instance", True),
            ("DEBUG: Calling generator.generate()", True),
            ("DEBUG: generator.generate() returned: 'Test output'", True),
            ("Generowanie API dla: test_spec", False),
            ("Test output", False)
        }
        
        # Check that all expected messages are in the actual calls
        for expected in expected_messages:
            assert expected in echo_messages, (
                f"Expected message not found: {expected}"
            )
        
        # Check that the generator was called
        mock_generator.generate.assert_called_once_with("test_spec")
