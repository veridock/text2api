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
    assert "version 0.1.6" in result.output


def test_generate_command_basic(mocker):
    """Test the generate command with a basic input."""
    # Create a mock for the FastAPIGenerator
    mock_generator = mocker.MagicMock()
    mock_generator.generate.return_value = [("test_file.py", "test content")]
    
    # Mock the extract_spec function
    mock_extract_spec = mocker.patch('text2api.cli.extract_spec')
    mock_extract_spec.return_value = {
        "name": "Test API",
        "description": "Test API description",
        "models": [{"name": "Item", "fields": []}]
    }
    
    # Mock the FastAPIGenerator class and other dependencies
    with mocker.patch('text2api.cli.FastAPIGenerator', return_value=mock_generator), \
         mocker.patch('os.makedirs'), \
         mocker.patch('os.path.exists', return_value=True):  # Mock path.exists to avoid file system checks
        
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Print the actual command being run
            cmd = [
                "generate", "server", "test_spec",
                "--output-dir", "./output",
                "--project-name", "test_project"
            ]
            print(f"\nRunning command: {' '.join(cmd)}")
            
            result = runner.invoke(cli_main, cmd, catch_exceptions=False)
            
            # Print debug information
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
            if result.exception:
                import traceback
                print("Traceback:")
                traceback.print_tb(result.exc_info[2])
            
            assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}. Output: {result.output}"
            assert "Generating FastAPI server for: test_spec" in result.output
            mock_generator.generate.assert_called_once()


def test_generate_command_with_debug(mocker, monkeypatch, capsys):
    """Test the generate command with debug output."""
    # Create a mock for the FastAPIGenerator
    mock_generator = mocker.MagicMock()
    mock_generator.generate.return_value = [("test_file.py", "test content")]
    
    # Mock the extract_spec function
    mock_extract_spec = mocker.patch('text2api.cli.extract_spec')
    mock_extract_spec.return_value = {
        "name": "Test API",
        "description": "Test API description",
        "models": [{"name": "Item", "fields": []}]
    }
    
    # Mock the FastAPIGenerator class and other dependencies
    with mocker.patch('text2api.cli.FastAPIGenerator', return_value=mock_generator), \
         mocker.patch('os.makedirs'), \
         mocker.patch('os.path.exists', return_value=True):  # Mock path.exists to avoid file system checks
        
        # Capture all echo calls
        echo_calls = []
        
        def mock_echo(message, **kwargs):
            echo_calls.append((message, kwargs.get('err', False)))
            # Also print to stdout for debugging
            print(f"ECHO: {message}")
        
        # Replace click.echo with our mock
        monkeypatch.setattr('click.echo', mock_echo)
        
        # Run the CLI command with debug flag
        runner = CliRunner()
        with runner.isolated_filesystem():
            cmd = [
                "--debug",  # Move debug flag to the beginning
                "generate", "server", "test_spec",
                "--output-dir", "./output",
                "--project-name", "test_project"
            ]
            print(f"\nRunning command: {' '.join(cmd)}")
            
            result = runner.invoke(cli_main, cmd, catch_exceptions=False)
            
            # Print captured output for debugging
            captured = capsys.readouterr()
            print("\n=== Captured Output ===")
            print(captured.out)
            print("=== End Captured Output ===\n")
            
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
            if result.exception:
                import traceback
                print("Traceback:")
                traceback.print_tb(result.exc_info[2])
            
            # Check the command executed successfully
            assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}. Output: {result.output}"
            
            # Convert echo calls to a set of (message, is_error) tuples for easier comparison
            echo_messages = set()
            for call in echo_calls:
                if len(call) == 2 and isinstance(call, tuple):
                    message, is_error = call
                    if message and message.strip():
                        echo_messages.add((message.strip(), is_error))
            
            # Print all captured echo messages for debugging
            print("\n=== Captured Echo Messages ===")
            for msg, is_err in sorted(echo_messages):
                print(f"{'ERROR' if is_err else 'OUTPUT'}: {msg}")
            print("=== End Captured Echo Messages ===\n")
            
            # Verify debug messages were printed
            expected_messages = {
                ("DEBUG: Output directory: ./output", True),
                ("Extracting API specification from description...", False),
                ("Extracted API Specification:", False),
                ("{\n  \"name\": \"Test API\",\n  \"description\": \"Test API description\",\n  \"models\": [\n    {\n      \"name\": \"Item\",\n      \"fields\": []\n    }\n  ]\n}", False),
                ("Generating FastAPI server code...", False),
                ("Generating FastAPI server for: test_spec", False),
                ("✅ Successfully generated FastAPI server at: [('test_file.py', 'test content')]", False),
                ("Next steps:", False),
                ("1. cd [('test_file.py', 'test content')]", False),
                ("2. pip install -r requirements.txt", False),
                ("3. uvicorn app.main:app --reload", False),
                ("Open http://localhost:8000/docs to view the API documentation", False)
            }
            
            # Check that all expected messages are in the actual output
            missing_messages = []
            for expected in expected_messages:
                if expected not in echo_messages:
                    missing_messages.append(expected)
            
            if missing_messages:
                print("\n=== Missing Expected Messages ===")
                for msg in missing_messages:
                    print(f"Missing: {msg}")
                print("=== End Missing Messages ===\n")
                
            # Only fail if we're missing messages
            if missing_messages:
                missing_list = "\n  " + "\n  ".join(str(msg) for msg in missing_messages)
                assert False, f"Missing {len(missing_messages)} expected messages in output:{missing_list}"
        
        # Check that the generator was called
        mock_generator.generate.assert_called_once()
