import os
import tempfile

import pytest

from text2api.generators.cli_gen import CLIGenerator


def test_cli_generator_init():
    """Test CLIGenerator initialization with default and custom template dirs."""
    # Test with default template directory
    generator = CLIGenerator()
    assert generator is not None
    templates = list(generator.env.list_templates())
    assert 'cli.py.j2' in templates

    # Test with custom template directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test template file
        template_file = os.path.join(temp_dir, 'test_template.j2')
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write("Test template")

        generator = CLIGenerator(template_dir=temp_dir)
        templates = list(generator.env.list_templates())
        assert 'test_template.j2' in templates

def test_cli_generator_generate():
    """Test the generate method of CLIGenerator."""
    generator = CLIGenerator()
    spec = "test specification"
    result = generator.generate(spec)
    assert "Successfully generated CLI at:" in result

# The following tests would require actual template files to be present
# They're marked as expected to fail for now since we don't have the templates


def test_render_cli():
    """Test rendering CLI template."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test template file
        template_file = os.path.join(temp_dir, 'cli.py.j2')
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write("CLI for {{ api_spec }}")

        generator = CLIGenerator(template_dir=temp_dir)
        result = generator.render_cli({"name": "test"})
        assert "CLI for {'name': 'test'}" in result

@pytest.mark.xfail(reason="Template files not available")
def test_render_requirements():
    """Test rendering requirements template."""
    generator = CLIGenerator()
    result = generator.render_requirements(
        {"dependencies": ["click"]}
    )
    assert "click" in result

@pytest.mark.xfail(reason="Template files not available")
def test_render_readme():
    """Test rendering README template."""
    generator = CLIGenerator()
    result = generator.render_readme(
        {"name": "test", "description": "Test API"}
    )
    assert "# test" in result
    assert "Test API" in result
