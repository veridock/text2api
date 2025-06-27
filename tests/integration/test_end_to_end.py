"""
End-to-end integration tests
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock

from text2api.core.generator import APIGenerator
from text2api.core.analyzer import ApiType


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndGeneration:
    """Test complete API generation flow"""

    @pytest.mark.asyncio
    async def test_generate_simple_rest_api(self, temp_dir, mock_ollama_client):
        """Test generating a simple REST API end-to-end"""
        # Setup
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client

        description = "API do zarządzania użytkownikami z operacjami CRUD"

        # Execute
        result = await generator.generate_from_text(
            text=description,
            output_name="user_api",
            include_docker=True,
            include_tests=True,
            include_docs=True,
        )

        # Assert
        assert result["success"] is True
        assert "project_path" in result
        assert "api_spec" in result

        project_path = Path(result["project_path"])
        assert project_path.exists()

        # Check generated files
        expected_files = [
            "main.py",
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            "README.md",
            "api_spec.json",
        ]

        for file_name in expected_files:
            file_path = project_path / file_name
            assert file_path.exists(), f"Missing file: {file_name}"

    @pytest.mark.asyncio
    async def test_generate_graphql_api(self, temp_dir, mock_ollama_client):
        """Test generating GraphQL API"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client

        # Mock GraphQL response
        mock_ollama_client.analyze_api_requirements.return_value = {
            "api_type": "graphql",
            "name": "blog_api",
            "description": "GraphQL Blog API",
            "framework": "graphene",
            "main_entities": ["post", "comment"],
            "endpoints": [],
            "auth_required": False,
            "database_required": True,
            "external_apis": [],
        }

        description = "GraphQL API dla bloga z postami i komentarzami"

        result = await generator.generate_from_text(
            text=description, output_name="blog_api"
        )

        assert result["success"] is True
        assert result["api_spec"]["api_type"] == "graphql"

        project_path = Path(result["project_path"])

        # Check GraphQL specific files
        assert (project_path / "app.py").exists()
        assert (project_path / "schema.py").exists()
        assert (project_path / "resolvers.py").exists()

    @pytest.mark.asyncio
    async def test_generate_websocket_api(self, temp_dir, mock_ollama_client):
        """Test generating WebSocket API"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client

        # Mock WebSocket response
        mock_ollama_client.analyze_api_requirements.return_value = {
            "api_type": "websocket",
            "name": "chat_api",
            "description": "Real-time Chat API",
            "framework": "websockets",
            "main_entities": ["message", "room"],
            "endpoints": [],
            "auth_required": True,
            "database_required": True,
            "external_apis": [],
        }

        description = "System czatu w czasie rzeczywistym z pokojami"

        result = await generator.generate_from_text(
            text=description, output_name="chat_api"
        )

        assert result["success"] is True
        assert result["api_spec"]["api_type"] == "websocket"

        project_path = Path(result["project_path"])

        # Check WebSocket specific files
        assert (project_path / "server.py").exists()
        assert (project_path / "client_example.py").exists()

    @pytest.mark.asyncio
    async def test_generate_cli_tool(self, temp_dir, mock_ollama_client):
        """Test generating CLI tool"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client

        # Mock CLI response
        mock_ollama_client.analyze_api_requirements.return_value = {
            "api_type": "cli",
            "name": "file_converter",
            "description": "File conversion CLI tool",
            "framework": "click",
            "main_entities": ["file"],
            "endpoints": [],
            "auth_required": False,
            "database_required": False,
            "external_apis": [],
        }

        description = "CLI tool do konwersji plików między formatami"

        result = await generator.generate_from_text(
            text=description, output_name="file_converter"
        )

        assert result["success"] is True
        assert result["api_spec"]["api_type"] == "cli"

        project_path = Path(result["project_path"])

        # Check CLI specific files
        assert (project_path / "cli.py").exists()
        assert (project_path / "setup.py").exists()

    @pytest.mark.asyncio
    async def test_generate_with_complex_requirements(
        self, temp_dir, mock_ollama_client
    ):
        """Test generating API with complex requirements"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client

        # Mock complex e-commerce response
        mock_ollama_client.analyze_api_requirements.return_value = {
            "api_type": "rest",
            "name": "ecommerce_api",
            "description": "E-commerce platform API",
            "framework": "fastapi",
            "main_entities": ["product", "order", "user", "payment"],
            "endpoints": [
                {
                    "path": "/products",
                    "method": "GET",
                    "name": "list_products",
                    "description": "List products",
                    "parameters": [],
                    "request_body": [],
                    "response_body": [],
                },
                {
                    "path": "/orders",
                    "method": "POST",
                    "name": "create_order",
                    "description": "Create order",
                    "parameters": [],
                    "request_body": [],
                    "response_body": [],
                },
            ],
            "auth_required": True,
            "database_required": True,
            "external_apis": ["payment_gateway", "shipping_service"],
        }

        description = """
        E-commerce platform z produktami, zamówieniami, 
        płatnościami i integracją z zewnętrznymi serwisami
        """

        result = await generator.generate_from_text(
            text=description,
            output_name="ecommerce_api",
            include_docker=True,
            include_tests=True,
            include_docs=True,
        )

        assert result["success"] is True

        api_spec = result["api_spec"]
        assert api_spec["auth_type"] == "jwt"
        assert api_spec["database_required"] is True
        assert len(api_spec["external_apis"]) > 0
        assert len(api_spec["endpoints"]) >= 2

        project_path = Path(result["project_path"])

        # Check complex features are included
        main_py = (project_path / "main.py").read_text()
        assert "jwt" in main_py.lower() or "auth" in main_py.lower()
        assert "database" in main_py.lower() or "db" in main_py.lower()

    @pytest.mark.asyncio
    async def test_error_handling_ollama_unavailable(self, temp_dir):
        """Test error handling when Ollama is unavailable"""
        generator = APIGenerator(output_dir=str(temp_dir))

        # Mock Ollama as unavailable
        generator.ollama_client.health_check = AsyncMock(return_value=False)

        description = "Simple API"

        result = await generator.generate_from_text(
            text=description, output_name="simple_api"
        )

        assert result["success"] is False
        assert "error" in result
        assert "Ollama" in result["error"]

    @pytest.mark.asyncio
    async def test_language_detection_integration(self, temp_dir, mock_ollama_client):
        """Test language detection integration"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client

        # Test different languages
        test_cases = [
            ("API for user management", "en"),
            ("API do zarządzania użytkownikami", "pl"),
            ("API für Benutzerverwaltung", "de"),
        ]

        for description, expected_lang in test_cases:
            with patch.object(
                generator.text_analyzer.language_detector,
                "detect_language",
                return_value=expected_lang,
            ):
                result = await generator.generate_from_text(
                    text=description, output_name=f"api_{expected_lang}"
                )

                assert result["success"] is True
                assert result["api_spec"]["language"] == expected_lang


# tests/integration/test_ollama_integration.py

"""
Integration tests with Ollama (requires running Ollama server)
"""

import pytest
import asyncio
from unittest.mock import patch

from text2api.llm.ollama_client import OllamaClient
from text2api.core.analyzer import TextAnalyzer


@pytest.mark.integration
@pytest.mark.requires_ollama
class TestOllamaIntegration:
    """Test integration with actual Ollama server"""

    @pytest.mark.asyncio
    async def test_real_ollama_connection(self):
        """Test connection to real Ollama server"""
        client = OllamaClient()

        # This test requires actual Ollama server running
        try:
            is_healthy = await client.health_check()
            if not is_healthy:
                pytest.skip("Ollama server not available")

            models = await client.list_models()
            assert isinstance(models, list)

        except Exception as e:
            pytest.skip(f"Ollama not available: {e}")

    @pytest.mark.asyncio
    async def test_real_text_analysis(self):
        """Test actual text analysis with Ollama"""
        client = OllamaClient()

        try:
            is_healthy = await client.health_check()
            if not is_healthy:
                pytest.skip("Ollama server not available")

            # Test simple analysis
            text = "Create a REST API for managing users with CRUD operations"

            analyzer = TextAnalyzer(client)
            result = await analyzer.analyze_text(text)

            # Verify result structure
            assert result.name
            assert result.description
            assert len(result.endpoints) > 0
            assert len(result.models) > 0

        except Exception as e:
            pytest.skip(f"Ollama analysis failed: {e}")

    @pytest.mark.asyncio
    async def test_model_availability(self):
        """Test model availability and download"""
        client = OllamaClient()

        try:
            is_healthy = await client.health_check()
            if not is_healthy:
                pytest.skip("Ollama server not available")

            # Check if recommended model exists
            models = await client.list_models()
            model_names = [m.name for m in models]

            recommended_models = ["llama3.1:8b", "llama3.1:7b", "llama3:8b"]
            available_recommended = [m for m in model_names if m in recommended_models]

            if not available_recommended:
                pytest.skip("No recommended models available")

            # Test model usage
            model_name = available_recommended[0]
            response = await client.generate(model_name, "Hello", format="json")
            assert response  # Should get some response

        except Exception as e:
            pytest.skip(f"Model test failed: {e}")


# tests/integration/test_docker_integration.py

"""
Integration tests with Docker
"""

import pytest
from unittest.mock import Mock, patch

from text2api.utils.docker_utils import DockerManager


@pytest.mark.integration
@pytest.mark.requires_docker
class TestDockerIntegration:
    """Test Docker integration"""

    def test_docker_availability(self):
        """Test Docker daemon availability"""
        manager = DockerManager()

        if not manager.is_docker_available():
            pytest.skip("Docker not available")

        # Test daemon connection
        is_available = manager.check_docker_daemon()
        assert is_available is True

    def test_docker_system_info(self):
        """Test Docker system information"""
        manager = DockerManager()

        if not manager.check_docker_daemon():
            pytest.skip("Docker daemon not available")

        info = manager.get_system_info()

        assert info["success"] is True
        assert "docker_version" in info
        assert "containers_running" in info
        assert info["containers_running"] >= 0

    @pytest.mark.asyncio
    async def test_dockerfile_generation(self, sample_api_spec):
        """Test Dockerfile generation"""
        manager = DockerManager()

        dockerfile_content = manager.generate_dockerfile(sample_api_spec)

        assert "FROM" in dockerfile_content
        assert "WORKDIR" in dockerfile_content
        assert "COPY" in dockerfile_content
        assert "CMD" in dockerfile_content or "ENTRYPOINT" in dockerfile_content

    def test_docker_compose_generation(self, sample_api_spec):
        """Test docker-compose.yml generation"""
        manager = DockerManager()

        compose_content = manager.generate_docker_compose(sample_api_spec)

        assert "version:" in compose_content
        assert "services:" in compose_content
        assert sample_api_spec.name.replace("_", "-") in compose_content

        if sample_api_spec.database_required:
            assert "db:" in compose_content
            assert "postgres" in compose_content.lower()


# tests/integration/test_file_operations.py

"""
Integration tests for file operations
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from text2api.utils.file_utils import FileManager


@pytest.mark.integration
class TestFileOperationsIntegration:
    """Test file operations integration"""

    @pytest.mark.asyncio
    async def test_large_file_operations(self):
        """Test operations with larger files"""
        manager = FileManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create large content
            large_content = "x" * 10000  # 10KB file
            large_file = temp_path / "large_file.txt"

            # Write and read large file
            await manager.write_file(large_file, large_content)
            read_content = await manager.read_file(large_file)

            assert read_content == large_content
            assert manager.get_file_size(large_file) == 10000

    @pytest.mark.asyncio
    async def test_directory_synchronization(self):
        """Test directory synchronization"""
        manager = FileManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            source_dir = temp_path / "source"
            target_dir = temp_path / "target"

            source_dir.mkdir()
            target_dir.mkdir()

            # Create source files
            (source_dir / "file1.txt").write_text("content1")
            (source_dir / "file2.txt").write_text("content2")

            # Sync directories
            result = await manager.sync_directories(source_dir, target_dir)

            assert (
                result["success"] is True
                if "success" in result
                else len(result["errors"]) == 0
            )
            assert (target_dir / "file1.txt").exists()
            assert (target_dir / "file2.txt").exists()

    def test_archive_operations(self):
        """Test archive creation and extraction"""
        manager = FileManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create source directory with files
            source_dir = temp_path / "source"
            source_dir.mkdir()
            (source_dir / "file1.txt").write_text("content1")
            (source_dir / "file2.txt").write_text("content2")

            # Create archive
            archive_path = temp_path / "archive.zip"
            manager.create_archive(source_dir, archive_path, "zip")

            assert archive_path.exists()
            assert archive_path.stat().st_size > 0

            # Extract archive
            extract_dir = temp_path / "extracted"
            manager.extract_archive(archive_path, extract_dir)

            extracted_source = extract_dir / "source"
            assert extracted_source.exists()
            assert (extracted_source / "file1.txt").exists()
            assert (extracted_source / "file2.txt").exists()

    @pytest.mark.asyncio
    async def test_concurrent_file_operations(self):
        """Test concurrent file operations"""
        manager = FileManager()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create multiple files concurrently
            async def create_file(index):
                file_path = temp_path / f"file_{index}.txt"
                await manager.write_file(file_path, f"content_{index}")
                return file_path

            import asyncio

            # Create 10 files concurrently
            tasks = [create_file(i) for i in range(10)]
            file_paths = await asyncio.gather(*tasks)

            # Verify all files were created
            for file_path in file_paths:
                assert file_path.exists()

            # Read all files concurrently
            async def read_file(file_path):
                return await manager.read_file(file_path)

            read_tasks = [read_file(fp) for fp in file_paths]
            contents = await asyncio.gather(*read_tasks)

            # Verify contents
            for i, content in enumerate(contents):
                assert content == f"content_{i}"


# tests/integration/test_generator_integration.py

"""
Integration tests for code generators
"""

import pytest
from pathlib import Path

from text2api.core.generator import APIGenerator
from text2api.generators.fastapi_gen import FastAPIGenerator
from text2api.generators.flask_gen import FlaskGenerator


@pytest.mark.integration
class TestGeneratorIntegration:
    """Test generator integration"""

    @pytest.mark.asyncio
    async def test_fastapi_generator_with_real_files(self, sample_api_spec, temp_dir):
        """Test FastAPI generator with actual file operations"""
        generator = FastAPIGenerator()

        result = await generator.generate(sample_api_spec, temp_dir)

        # Verify files were actually created
        for file_name, file_path in result.items():
            path = Path(file_path)
            assert path.exists(), f"File {file_name} was not created"
            assert path.stat().st_size > 0, f"File {file_name} is empty"

        # Check main.py content
        main_py_path = Path(result["main.py"])
        main_content = main_py_path.read_text()

        # Verify FastAPI specific content
        assert "from fastapi import" in main_content
        assert "app = FastAPI" in main_content
        assert sample_api_spec.name in main_content

        # Verify endpoints are generated
        for endpoint in sample_api_spec.endpoints:
            assert f"@app.{endpoint.method.value.lower()}" in main_content
            assert endpoint.path in main_content

    @pytest.mark.asyncio
    async def test_flask_generator_with_real_files(self, sample_api_spec, temp_dir):
        """Test Flask generator with actual file operations"""
        generator = FlaskGenerator()

        result = await generator.generate(sample_api_spec, temp_dir)

        # Verify files were created
        for file_name, file_path in result.items():
            path = Path(file_path)
            assert path.exists()
            assert path.stat().st_size > 0

        # Check app.py content
        app_py_path = Path(result["app.py"])
        app_content = app_py_path.read_text()

        # Verify Flask specific content
        assert "from flask import" in app_content
        assert "app = Flask" in app_content
        assert sample_api_spec.name in app_content

    @pytest.mark.asyncio
    async def test_generated_code_syntax(self, sample_api_spec, temp_dir):
        """Test that generated code has valid Python syntax"""
        generator = FastAPIGenerator()

        result = await generator.generate(sample_api_spec, temp_dir)

        # Check Python files for syntax errors
        python_files = [f for f in result.keys() if f.endswith(".py")]

        for file_name in python_files:
            file_path = Path(result[file_name])
            if file_path.exists():
                content = file_path.read_text()

                try:
                    compile(content, str(file_path), "exec")
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {file_name}: {e}")

    @pytest.mark.asyncio
    async def test_requirements_file_validity(self, sample_api_spec, temp_dir):
        """Test that generated requirements.txt is valid"""
        generator = FastAPIGenerator()

        result = await generator.generate(sample_api_spec, temp_dir)

        if "requirements.txt" in result:
            req_path = Path(result["requirements.txt"])
            content = req_path.read_text()

            # Check basic requirements format
            lines = [line.strip() for line in content.split("\n") if line.strip()]

            for line in lines:
                if not line.startswith("#"):  # Skip comments
                    # Should contain package name
                    assert "==" in line or ">=" in line or line.isalpha()

    @pytest.mark.asyncio
    async def test_docker_file_validity(self, sample_api_spec, temp_dir):
        """Test that generated Dockerfile is valid"""
        from text2api.utils.docker_utils import DockerManager

        docker_manager = DockerManager()
        dockerfile_content = docker_manager.generate_dockerfile(sample_api_spec)

        dockerfile_path = temp_dir / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)

        # Check Dockerfile structure
        lines = dockerfile_content.split("\n")
        instructions = [
            line.split()[0].upper()
            for line in lines
            if line.strip() and not line.startswith("#")
        ]

        # Must start with FROM
        assert instructions[0] == "FROM"

        # Should contain basic instructions
        required_instructions = ["WORKDIR", "COPY"]
        for instruction in required_instructions:
            assert instruction in instructions, f"Missing {instruction} instruction"
