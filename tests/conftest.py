import pytest
from pathlib import Path

@pytest.fixture
def test_project_dir(tmp_path):
    """Temporary directory for test projects."""
    return tmp_path

@pytest.fixture
def test_api_spec():
    """Sample API specification for testing."""
    return {
        "name": "test_api",
        "description": "Test API for testing purposes",
        "endpoints": [
            {
                "path": "/items",
                "method": "GET",
                "description": "Get all items",
                "responses": ["200"]
            },
            {
                "path": "/items/{id}",
                "method": "POST",
                "description": "Create an item",
                "responses": ["201"]
            }
        ]
    }

@pytest.fixture
def test_env_file(test_project_dir):
    """Create a sample .env file for testing."""
    env_path = test_project_dir / ".env"
    env_content = """
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///test.db
HOST=localhost
PORT=5000
DEBUG=True
    """
    env_path.write_text(env_content)
    return env_path
