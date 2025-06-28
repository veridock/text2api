"""Integration tests for the FastAPI server generation workflow."""

import os
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from text2api.cli import main as cli_main

# Sample API specification for testing
SAMPLE_SPEC = """
A simple todo API with the following endpoints:
- GET /todos - List all todos
- POST /todos - Create a new todo
- GET /todos/{id} - Get a specific todo
- PUT /todos/{id} - Update a todo
- DELETE /todos/{id} - Delete a todo

Each todo has:
- id: string (auto-generated)
- title: string
- description: string (optional)
- completed: boolean (default: false)
"""

@pytest.fixture
def sample_spec_file(tmp_path):
    """Create a temporary file with sample API specification."""
    spec_file = tmp_path / "api_spec.txt"
    spec_file.write_text(SAMPLE_SPEC)
    return spec_file


def test_generate_fastapi_server(tmp_path, sample_spec_file, monkeypatch):
    """Test generating a FastAPI server from a spec file."""
    # Setup
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Mock the extract_spec function to return a consistent result
    mock_spec = {
        "name": "Todo API",
        "description": "A simple todo API",
        "endpoints": [
            {
                "method": "GET",
                "path": "/todos",
                "description": "List all todos",
                "responses": {"200": {"description": "List of todos"}}
            },
            {
                "method": "POST",
                "path": "/todos",
                "description": "Create a new todo",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "completed": {"type": "boolean"}
                                },
                                "required": ["title"]
                            }
                        }
                    }
                },
                "responses": {"201": {"description": "Created todo"}}
            }
        ]
    }
    
    # Mock the generator to avoid actual file system operations
    mock_generator = MagicMock()
    mock_generator.generate.return_value = [
        ("app/main.py", "# Mock FastAPI app code"),
        ("requirements.txt", "fastapi\nuvicorn"),
        ("README.md", "# Todo API\n\nA simple todo API")
    ]
    
    # Patch the necessary functions and classes
    with patch('text2api.cli.extract_spec', return_value=mock_spec), \
         patch('text2api.cli.FastAPIGenerator', return_value=mock_generator), \
         patch('os.makedirs'):
        
        # Run the CLI command
        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            [
                'generate', 'server',
                str(sample_spec_file),
                '--output-dir', str(output_dir),
                '--project-name', 'test-todo-api'
            ]
        )
        
        # Verify the command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Verify the generator was called with the correct arguments
        from text2api.cli import FastAPIGenerator
        FastAPIGenerator.assert_called_once()
        
        # Verify the generator's generate method was called
        mock_generator.generate.assert_called_once()
        
        # Verify the output directory was created
        assert output_dir.exists()
        
        # Verify the success message was printed
        assert "Successfully generated FastAPI server" in result.output
        # The output shows the generated files, not the output directory
        assert "app/main.py" in result.output
        assert "requirements.txt" in result.output
        assert "README.md" in result.output


def test_generate_fastapi_server_with_debug(tmp_path, sample_spec_file, monkeypatch):
    """Test generating a FastAPI server with debug output."""
    # Setup
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Mock the extract_spec function
    mock_spec = {"name": "Test API", "description": "Test description", "endpoints": []}
    
    # Mock the generator
    mock_generator = MagicMock()
    mock_generator.generate.return_value = [("test.py", "test")]
    
    # Capture debug output
    debug_output = []
    
    def mock_echo(message, **kwargs):
        debug_output.append((message, kwargs.get('err', False)))
    
    monkeypatch.setattr('click.echo', mock_echo)
    
    # Patch the necessary functions and classes
    with patch('text2api.cli.extract_spec', return_value=mock_spec), \
         patch('text2api.cli.FastAPIGenerator', return_value=mock_generator), \
         patch('os.makedirs'):
        
        # Run the CLI command with debug flag
        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            [
                '--debug',
                'generate', 'server',
                str(sample_spec_file),
                '--output-dir', str(output_dir),
                '--project-name', 'test-debug-api'
            ]
        )
        
        # Verify the command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Convert debug output to a set of (message, is_error) tuples
        debug_messages = set()
        for msg, is_err in debug_output:
            if msg and msg.strip():
                debug_messages.add((msg.strip(), is_err))
        
        # Verify debug messages were printed
        # Note: The actual CLI only shows some debug messages
        expected_debug = {
            (f"DEBUG: Output directory: {str(output_dir)}", True),
            ("Extracting API specification from description...", False),
            ("Generating FastAPI server code...", False)
        }
        
        # Check that all expected debug messages are present
        for expected in expected_debug:
            assert expected in debug_messages, f"Expected debug message not found: {expected}"


def test_generate_fastapi_server_with_invalid_spec(tmp_path):
    """Test generating a FastAPI server with an invalid spec."""
    # Create an empty spec file
    spec_file = tmp_path / "invalid_spec.txt"
    spec_file.write_text("")
    
    # Setup output directory
    output_dir = tmp_path / "output"
    
    # Run the CLI command
    runner = CliRunner()
    result = runner.invoke(
        cli_main,
        [
            'generate', 'server',
            str(spec_file),
            '--output-dir', str(output_dir),
            '--project-name', 'test-invalid-spec'
        ]
    )
    
    # Verify the command failed with an error
    assert result.exit_code != 0
    assert "Error" in result.output or "error" in result.output.lower()


def test_generate_fastapi_server_with_existing_output_dir(tmp_path, sample_spec_file, monkeypatch):
    """Test generating a FastAPI server with an existing output directory."""
    # Setup
    output_dir = tmp_path / "existing_output"
    output_dir.mkdir()
    
    # Create a file in the output directory
    (output_dir / "existing_file.txt").write_text("test")
    
    # Mock the extract_spec function
    mock_spec = {"name": "Test API", "description": "Test description", "endpoints": []}
    
    # Mock the generator
    mock_generator = MagicMock()
    mock_generator.generate.return_value = [("test.py", "test")]
    
    # Patch the necessary functions and classes
    with patch('text2api.cli.extract_spec', return_value=mock_spec), \
         patch('text2api.cli.FastAPIGenerator', return_value=mock_generator), \
         patch('os.makedirs') as mock_makedirs, \
         patch('os.path.exists', lambda x: str(x).endswith('existing_output')):
        
        # Run the CLI command
        runner = CliRunner()
        result = runner.invoke(
            cli_main,
            [
                'generate', 'server',
                str(sample_spec_file),
                '--output-dir', str(output_dir),
                '--project-name', 'test-existing-dir'
            ]
        )
        
        # The CLI should still work even if the directory exists
        assert result.exit_code == 0
        assert "Successfully generated FastAPI server" in result.output
        
        # Verify the generator was called
        mock_generator.generate.assert_called_once()
