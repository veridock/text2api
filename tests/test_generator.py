"""
Tests for the APIGenerator class.
"""
import pytest
from pathlib import Path
from text2api.core.generator import APIGenerator

class TestAPIGenerator:
    """Test cases for APIGenerator class."""
    
    @pytest.fixture
    def generator(self, tmp_path):
        """Create an APIGenerator instance with a temporary output directory."""
        return APIGenerator(output_dir=str(tmp_path / "output"))
    
    def test_initialization(self, generator):
        """Test that APIGenerator initializes correctly."""
        assert generator is not None
        assert isinstance(generator.output_dir, Path)
        assert generator.output_dir.exists()
    
    def test_validate_description(self, generator):
        """Test description validation."""
        # Valid descriptions
        assert generator.validate_description("Create a simple REST API") is True
        assert generator.validate_description("Generate a GraphQL API with users and posts") is True
        
        # Invalid descriptions
        assert generator.validate_description("") is False
        assert generator.validate_description("  ") is False
        assert generator.validate_description("API") is False  # Too short
    
    def test_list_supported_frameworks(self, generator):
        """Test listing supported frameworks."""
        frameworks = generator.list_supported_frameworks()
        
        assert isinstance(frameworks, dict)
        assert "rest" in frameworks
        assert "graphql" in frameworks
        assert "grpc" in frameworks
        assert "websocket" in frameworks
        assert "cli" in frameworks
        
        # Check some framework examples
        assert "fastapi" in frameworks["rest"]
        assert "flask" in frameworks["rest"]
        assert "strawberry" in frameworks["graphql"]
        assert "click" in frameworks["cli"]
    
    def test_generate_basic(self, generator):
        """Test basic API generation."""
        description = "A simple todo list API"
        result = generator.generate(
            description=description,
            api_type="rest",
            framework="fastapi"
        )
        
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["api_type"] == "rest"
        assert result["framework"] == "fastapi"
        assert "project_dir" in result
        assert "files_generated" in result
        assert isinstance(result["files_generated"], list)
