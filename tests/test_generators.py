import pytest
from text2api.generators import FlaskGenerator, FastAPIGenerator
from text2api.core import TextAnalyzer
from pathlib import Path

def test_flask_generator(test_project_dir):
    generator = FlaskGenerator()
    analyzer = TextAnalyzer()
    spec = analyzer.analyze("Create a simple REST API for managing users")
    
    generator.generate(spec, test_project_dir)
    
    assert (test_project_dir / "app.py").exists()
    assert (test_project_dir / "requirements.txt").exists()
    assert (test_project_dir / ".env").exists()

def test_fastapi_generator(test_project_dir):
    generator = FastAPIGenerator()
    analyzer = TextAnalyzer()
    spec = analyzer.analyze("Create a FastAPI service for managing products")
    
    generator.generate(spec, test_project_dir)
    
    assert (test_project_dir / "app.py").exists()
    assert (test_project_dir / "models.py").exists()
    assert (test_project_dir / "requirements.txt").exists()

def test_graphql_generator(test_project_dir):
    generator = GraphQLGenerator()
    analyzer = TextAnalyzer()
    spec = analyzer.analyze("Create a GraphQL API for a blog")
    
    generator.generate(spec, test_project_dir)
    
    assert (test_project_dir / "schema.py").exists()
    assert (test_project_dir / "resolvers.py").exists()
    assert (test_project_dir / "app.py").exists()

def test_grpc_generator(test_project_dir):
    generator = GRPCGenerator()
    analyzer = TextAnalyzer()
    spec = analyzer.analyze("Create a gRPC service for user management")
    
    generator.generate(spec, test_project_dir)
    
    assert (test_project_dir / "service.proto").exists()
    assert (test_project_dir / "server.py").exists()
    assert (test_project_dir / "client.py").exists()

def test_websocket_generator(test_project_dir):
    generator = WebSocketGenerator()
    analyzer = TextAnalyzer()
    spec = analyzer.analyze("Create a WebSocket chat application")
    
    generator.generate(spec, test_project_dir)
    
    assert (test_project_dir / "server.py").exists()
    assert (test_project_dir / "client.py").exists()
    assert (test_project_dir / "requirements.txt").exists()

def test_cli_generator(test_project_dir):
    generator = CLIGenerator()
    analyzer = TextAnalyzer()
    spec = analyzer.analyze("Create a CLI tool for managing tasks")
    
    generator.generate(spec, test_project_dir)
    
    assert (test_project_dir / "cli.py").exists()
    assert (test_project_dir / "setup.py").exists()
    assert (test_project_dir / "requirements.txt").exists()
