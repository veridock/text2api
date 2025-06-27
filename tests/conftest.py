"""
Unit tests for TextAnalyzer
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch

from text2api.core.analyzer import TextAnalyzer, ApiSpec, ApiType, HttpMethod
from text2api.llm.ollama_client import OllamaClient


@pytest.mark.unit
class TestTextAnalyzer:
    """Test cases for TextAnalyzer"""

    def test_init(self, mock_ollama_client):
        """Test TextAnalyzer initialization"""
        analyzer = TextAnalyzer(mock_ollama_client)
        assert analyzer.ollama_client == mock_ollama_client
        assert analyzer.language_detector is not None
        assert analyzer.patterns is not None

    @pytest.mark.asyncio
    async def test_analyze_text_simple(self, mock_ollama_client):
        """Test simple text analysis"""
        # Setup
        analyzer = TextAnalyzer(mock_ollama_client)
        text = "API do zarządzania użytkownikami z operacjami CRUD"

        # Mock Ollama response
        ollama_response = {
            "api_type": "rest",
            "name": "user_management_api",
            "description": "API do zarządzania użytkownikami",
            "framework": "fastapi",
            "entities": ["user"],
            "endpoints": [
                {
                    "path": "/users",
                    "method": "GET",
                    "name": "list_users",
                    "description": "List users",
                    "parameters": [],
                    "request_body": [],
                    "response_body": [],
                }
            ],
            "auth_required": True,
            "database_required": True,
            "external_apis": [],
        }

        mock_ollama_client.analyze_api_requirements.return_value = ollama_response

        # Execute
        result = await analyzer.analyze_text(text)

        # Assert
        assert isinstance(result, ApiSpec)
        assert result.name == "user_management_api"
        assert result.api_type == ApiType.REST
        assert result.framework == "fastapi"
        assert len(result.endpoints) > 0
        assert result.database_required is True

    @pytest.mark.asyncio
    async def test_analyze_text_with_language_detection(self, mock_ollama_client):
        """Test text analysis with language detection"""
        analyzer = TextAnalyzer(mock_ollama_client)

        # Test different languages
        test_cases = [
            ("API for user management with CRUD operations", "en"),
            ("API do zarządzania użytkownikami", "pl"),
            ("API für Benutzerverwaltung", "de"),
        ]

        for text, expected_lang in test_cases:
            with patch.object(
                analyzer.language_detector,
                "detect_language",
                return_value=expected_lang,
            ):
                result = await analyzer.analyze_text(text)
                assert result.language == expected_lang

    def test_analyze_patterns_crud(self, mock_ollama_client):
        """Test pattern analysis for CRUD operations"""
        analyzer = TextAnalyzer(mock_ollama_client)

        test_cases = [
            ("create and delete users", ["create", "delete"]),
            ("read and update products", ["read", "update"]),
            ("full CRUD operations", ["create", "read", "update", "delete"]),
        ]

        for text, expected_ops in test_cases:
            result = analyzer._analyze_patterns(text)
            for op in expected_ops:
                assert op in result["crud_operations"]

    def test_analyze_patterns_entities(self, mock_ollama_client):
        """Test pattern analysis for entities"""
        analyzer = TextAnalyzer(mock_ollama_client)

        text = "manage users, products, and orders"
        result = analyzer._analyze_patterns(text)

        expected_entities = ["user", "product", "order"]
        for entity in expected_entities:
            assert entity in result["entities"]

    def test_analyze_patterns_api_type(self, mock_ollama_client):
        """Test API type detection from patterns"""
        analyzer = TextAnalyzer(mock_ollama_client)

        test_cases = [
            ("REST API with HTTP endpoints", ApiType.REST),
            ("GraphQL API with queries and mutations", ApiType.GRAPHQL),
            ("real-time chat with websockets", ApiType.WEBSOCKET),
            ("command line tool", ApiType.CLI),
            ("gRPC microservice", ApiType.GRPC),
        ]

        for text, expected_type in test_cases:
            result = analyzer._analyze_patterns(text)
            assert result["api_type"] == expected_type

    def test_create_endpoints_from_entities(self, mock_ollama_client):
        """Test endpoint creation from entities"""
        analyzer = TextAnalyzer(mock_ollama_client)

        entities = ["user", "product"]
        crud_ops = ["create", "read", "update", "delete"]

        endpoints = analyzer._generate_crud_endpoints(entities, crud_ops)

        # Should generate endpoints for each entity and operation
        assert len(endpoints) >= len(entities) * len(crud_ops)

        # Check for specific endpoints
        endpoint_names = [ep.name for ep in endpoints]
        assert "create_user" in endpoint_names
        assert "list_users" in endpoint_names
        assert "get_user" in endpoint_names
        assert "update_user" in endpoint_names
        assert "delete_user" in endpoint_names

    def test_create_models_from_entities(self, mock_ollama_client):
        """Test model creation from entities"""
        analyzer = TextAnalyzer(mock_ollama_client)

        entities = ["user", "product"]
        models = analyzer._create_models(entities, [])

        assert len(models) == len(entities)

        # Check model structure
        user_model = next(m for m in models if m["name"] == "User")
        assert user_model is not None

        field_names = [f["name"] for f in user_model["fields"]]
        assert "id" in field_names
        assert "name" in field_names
        assert "created_at" in field_names

    @pytest.mark.asyncio
    async def test_analyze_text_ollama_error(self, mock_ollama_client):
        """Test handling of Ollama errors"""
        analyzer = TextAnalyzer(mock_ollama_client)

        # Mock Ollama error
        mock_ollama_client.analyze_api_requirements.side_effect = Exception(
            "Ollama error"
        )

        text = "API for user management"
        result = await analyzer.analyze_text(text)

        # Should use fallback analysis
        assert isinstance(result, ApiSpec)
        assert result.name  # Should have some generated name

    def test_extract_name_from_text(self, mock_ollama_client):
        """Test name extraction from text"""
        analyzer = TextAnalyzer(mock_ollama_client)

        test_cases = [
            ("User management API", "user_management"),
            ("Create a blog API", "create_blog"),
            ("E-commerce platform", "e_commerce_platform"),
        ]

        for text, expected_name in test_cases:
            result = analyzer._extract_name_from_text(text)
            assert expected_name in result or result == "generated_api"


# tests/unit/test_ollama_client.py

"""
Unit tests for OllamaClient
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
import httpx

from text2api.llm.ollama_client import OllamaClient, OllamaModel


@pytest.mark.unit
class TestOllamaClient:
    """Test cases for OllamaClient"""

    def test_init(self):
        """Test OllamaClient initialization"""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"

        custom_client = OllamaClient("http://custom:11434")
        assert custom_client.base_url == "http://custom:11434"

    @pytest.mark.asyncio
    async def test_generate_success(self):
        """Test successful generation"""
        client = OllamaClient()

        mock_response = Mock()
        mock_response.json.return_value = {"response": "Generated text"}
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await client.generate("llama3.1:8b", "Test prompt")
            assert result == "Generated text"

    @pytest.mark.asyncio
    async def test_generate_with_format(self):
        """Test generation with JSON format"""
        client = OllamaClient()

        mock_response = Mock()
        mock_response.json.return_value = {"response": '{"key": "value"}'}
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await client.generate("llama3.1:8b", "Test prompt", format="json")
            assert result == '{"key": "value"}'

    @pytest.mark.asyncio
    async def test_generate_http_error(self):
        """Test generation with HTTP error"""
        client = OllamaClient()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.HTTPError("Connection failed")
            )

            with pytest.raises(Exception) as exc_info:
                await client.generate("llama3.1:8b", "Test prompt")

            assert "Błąd komunikacji z Ollama" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_chat(self):
        """Test chat functionality"""
        client = OllamaClient()

        mock_response = Mock()
        mock_response.json.return_value = {"message": {"content": "Chat response"}}
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            messages = [{"role": "user", "content": "Hello"}]
            result = await client.chat("llama3.1:8b", messages)
            assert result == "Chat response"

    @pytest.mark.asyncio
    async def test_list_models(self):
        """Test listing models"""
        client = OllamaClient()

        mock_response = Mock()
        mock_response.json.return_value = {
            "models": [
                {
                    "name": "llama3.1:8b",
                    "size": "4.7GB",
                    "digest": "abc123",
                    "modified_at": "2024-01-01T00:00:00Z",
                }
            ]
        }
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            models = await client.list_models()
            assert len(models) == 1
            assert isinstance(models[0], OllamaModel)
            assert models[0].name == "llama3.1:8b"

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        client = OllamaClient()

        mock_response = Mock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await client.health_check()
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test failed health check"""
        client = OllamaClient()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.ConnectError("Connection failed")
            )

            result = await client.health_check()
            assert result is False

    def test_clean_json_response(self):
        """Test JSON response cleaning"""
        client = OllamaClient()

        test_cases = [
            ('```json\n{"key": "value"}\n```', '{"key": "value"}'),
            ('Some text before {"key": "value"} some text after', '{"key": "value"}'),
            ('{"valid": "json"}', '{"valid": "json"}'),
        ]

        for input_text, expected in test_cases:
            result = client._clean_json_response(input_text)
            assert result == expected

    @pytest.mark.asyncio
    async def test_analyze_api_requirements(self):
        """Test API requirements analysis"""
        client = OllamaClient()

        # Mock successful model check and generation
        with patch.object(client, "ensure_model", return_value=True), patch.object(
            client, "generate", return_value='{"api_type": "rest"}'
        ):
            result = await client.analyze_api_requirements("Test API description")
            assert result["api_type"] == "rest"

    @pytest.mark.asyncio
    async def test_analyze_api_requirements_invalid_json(self):
        """Test API analysis with invalid JSON response"""
        client = OllamaClient()

        with patch.object(client, "ensure_model", return_value=True), patch.object(
            client, "generate", return_value="Invalid JSON"
        ), patch.object(client, "_clean_json_response", return_value="Still invalid"):
            result = await client.analyze_api_requirements("Test API description")
            # Should return fallback analysis
            assert "api_type" in result
            assert result["api_type"] == "rest"


# tests/unit/test_language_detector.py

"""
Unit tests for LanguageDetector
"""

import pytest
from unittest.mock import patch

from text2api.llm.language_detector import LanguageDetector


@pytest.mark.unit
class TestLanguageDetector:
    """Test cases for LanguageDetector"""

    def test_init(self):
        """Test LanguageDetector initialization"""
        detector = LanguageDetector()
        assert detector.language_patterns is not None
        assert detector.language_names is not None
        assert "pl" in detector.language_patterns
        assert "en" in detector.language_patterns

    def test_detect_language_polish(self):
        """Test Polish language detection"""
        detector = LanguageDetector()

        polish_texts = [
            "API do zarządzania użytkownikami z operacjami CRUD",
            "System czatu w czasie rzeczywistym z pokojami",
            "Aplikacja e-commerce z produktami i zamówieniami",
        ]

        for text in polish_texts:
            with patch("langdetect.detect", return_value="pl"):
                result = detector.detect_language(text)
                assert result == "pl"

    def test_detect_language_english(self):
        """Test English language detection"""
        detector = LanguageDetector()

        english_texts = [
            "API for user management with CRUD operations",
            "Real-time chat system with rooms",
            "E-commerce application with products and orders",
        ]

        for text in english_texts:
            with patch("langdetect.detect", return_value="en"):
                result = detector.detect_language(text)
                assert result == "en"

    def test_detect_language_short_text(self):
        """Test language detection for short text"""
        detector = LanguageDetector()

        short_text = "API"
        result = detector.detect_language(short_text)
        assert result == "en"  # Default for short texts

    def test_detect_language_with_patterns(self):
        """Test language detection using patterns"""
        detector = LanguageDetector()

        # Test with mixed content where pattern validation is important
        test_cases = [
            ("Zarządzanie użytkowników w systemie", "pl"),
            ("User management in the system", "en"),
            ("Verwaltung von Benutzern im System", "de"),
        ]

        for text, expected_lang in test_cases:
            with patch("langdetect.detect", return_value=expected_lang):
                result = detector.detect_language(text)
                assert result == expected_lang

    def test_validate_with_patterns(self):
        """Test pattern validation"""
        detector = LanguageDetector()

        polish_text = "System zarządzania użytkownikami z bazą danych"
        score = detector._validate_with_patterns(polish_text, "pl")
        assert score > 0  # Should find some Polish patterns

        english_text = "User management system with database"
        score = detector._validate_with_patterns(english_text, "en")
        assert score > 0  # Should find some English patterns

    def test_get_language_info(self):
        """Test getting language information"""
        detector = LanguageDetector()

        text = "API do zarządzania użytkownikami"

        with patch.object(detector, "detect_language", return_value="pl"), patch.object(
            detector, "get_confidence", return_value=0.8
        ):
            info = detector.get_language_info(text)

            assert info["language"] == "pl"
            assert info["language_name"] == "Polski"
            assert info["confidence"] == 0.8
            assert "text_length" in info
            assert "word_count" in info

    def test_suggest_improvements(self):
        """Test improvement suggestions"""
        detector = LanguageDetector()

        # Test short text
        short_text = "API"
        suggestions = detector.suggest_improvements(short_text)
        assert any("krótki" in s or "short" in s for s in suggestions)

        # Test mixed language text
        with patch.object(detector, "_check_mixed_languages", return_value=0.6):
            mixed_text = "API for users and zarządzanie produktami"
            suggestions = detector.suggest_improvements(mixed_text)
            assert any("mieszank" in s or "mixed" in s for s in suggestions)

    def test_is_supported_language(self):
        """Test supported language check"""
        detector = LanguageDetector()

        assert detector.is_supported_language("pl") is True
        assert detector.is_supported_language("en") is True
        assert detector.is_supported_language("xyz") is False


# tests/unit/test_file_utils.py

"""
Unit tests for FileManager
"""

import pytest
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from text2api.utils.file_utils import FileManager


@pytest.mark.unit
class TestFileManager:
    """Test cases for FileManager"""

    def test_init(self):
        """Test FileManager initialization"""
        manager = FileManager()
        assert manager.temp_dir.exists()

    @pytest.mark.asyncio
    async def test_ensure_directory(self, temp_dir):
        """Test directory creation"""
        manager = FileManager()

        test_dir = temp_dir / "test_subdir"
        result = await manager.ensure_directory(test_dir)

        assert result == test_dir
        assert test_dir.exists()
        assert test_dir.is_dir()

    @pytest.mark.asyncio
    async def test_write_and_read_file(self, temp_dir):
        """Test file writing and reading"""
        manager = FileManager()

        test_file = temp_dir / "test.txt"
        test_content = "Hello, World!"

        # Write file
        await manager.write_file(test_file, test_content)
        assert test_file.exists()

        # Read file
        content = await manager.read_file(test_file)
        assert content == test_content

    @pytest.mark.asyncio
    async def test_write_and_read_json(self, temp_dir):
        """Test JSON file operations"""
        manager = FileManager()

        test_file = temp_dir / "test.json"
        test_data = {"key": "value", "number": 42}

        # Write JSON
        await manager.write_json(test_file, test_data)
        assert test_file.exists()

        # Read JSON
        data = await manager.read_json(test_file)
        assert data == test_data

    @pytest.mark.asyncio
    async def test_write_and_read_yaml(self, temp_dir):
        """Test YAML file operations"""
        manager = FileManager()

        test_file = temp_dir / "test.yaml"
        test_data = {"key": "value", "list": [1, 2, 3]}

        # Write YAML
        await manager.write_yaml(test_file, test_data)
        assert test_file.exists()

        # Read YAML
        data = await manager.read_yaml(test_file)
        assert data == test_data

    def test_copy_file(self, temp_dir):
        """Test file copying"""
        manager = FileManager()

        # Create source file
        src_file = temp_dir / "source.txt"
        src_file.write_text("Test content")

        dst_file = temp_dir / "destination.txt"

        # Copy file
        manager.copy_file(src_file, dst_file)

        assert dst_file.exists()
        assert dst_file.read_text() == "Test content"

    def test_list_files(self, temp_dir):
        """Test file listing"""
        manager = FileManager()

        # Create test files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.py").write_text("content2")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file3.txt").write_text("content3")

        # List all files
        files = manager.list_files(temp_dir, "*", recursive=False)
        txt_files = [f for f in files if f.suffix == ".txt"]
        assert len(txt_files) == 1

        # List recursively
        files_recursive = manager.list_files(temp_dir, "*.txt", recursive=True)
        assert len(files_recursive) == 2

    def test_file_info(self, temp_dir):
        """Test file information retrieval"""
        manager = FileManager()

        test_file = temp_dir / "test.txt"
        test_file.write_text("Test content")

        info = manager.get_file_info(test_file)

        assert info["exists"] is True
        assert info["name"] == "test.txt"
        assert info["size"] > 0
        assert info["is_file"] is True
        assert info["extension"] == ".txt"

    def test_file_info_nonexistent(self, temp_dir):
        """Test file info for nonexistent file"""
        manager = FileManager()

        nonexistent_file = temp_dir / "nonexistent.txt"
        info = manager.get_file_info(nonexistent_file)

        assert info["exists"] is False

    @pytest.mark.asyncio
    async def test_backup_and_restore(self, temp_dir):
        """Test file backup and restore"""
        manager = FileManager()

        original_file = temp_dir / "original.txt"
        original_content = "Original content"
        await manager.write_file(original_file, original_content)

        # Create backup
        backup_file = await manager.backup_file(original_file)
        assert backup_file.exists()
        assert backup_file.read_text() == original_content

        # Modify original
        await manager.write_file(original_file, "Modified content")

        # Restore from backup
        restored_file = await manager.restore_backup(backup_file)
        assert restored_file.read_text() == original_content
        assert not backup_file.exists()  # Backup should be removed

    def test_format_file_size(self):
        """Test file size formatting"""
        manager = FileManager()

        test_cases = [
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB"),
            (500, "500.0 B"),
        ]

        for size, expected in test_cases:
            result = manager.format_file_size(size)
            assert result == expected

    def test_find_files_by_content(self, temp_dir):
        """Test finding files by content"""
        manager = FileManager()

        # Create test files
        (temp_dir / "file1.py").write_text("def hello(): pass")
        (temp_dir / "file2.py").write_text("class MyClass: pass")
        (temp_dir / "file3.txt").write_text("hello world")

        # Search for files containing "hello"
        matching_files = manager.find_files_by_content(temp_dir, "hello", "*.py")

        assert len(matching_files) == 1
        assert matching_files[0].name == "file1.py"

    def test_calculate_directory_size(self, temp_dir):
        """Test directory size calculation"""
        manager = FileManager()

        # Create test files
        (temp_dir / "file1.txt").write_text("a" * 100)
        (temp_dir / "file2.txt").write_text("b" * 200)

        total_size = manager.calculate_directory_size(temp_dir)
        assert total_size >= 300  # At least 300 bytes


# tests/unit/test_generators.py

"""
Unit tests for code generators
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from text2api.generators.fastapi_gen import FastAPIGenerator
from text2api.generators.flask_gen import FlaskGenerator
from text2api.generators.graphql_gen import GraphQLGenerator
from text2api.generators.grpc_gen import GRPCGenerator
from text2api.generators.websocket_gen import WebSocketGenerator
from text2api.generators.cli_gen import CLIGenerator
from text2api.core.analyzer import ApiSpec, ApiType


@pytest.mark.unit
class TestFastAPIGenerator:
    """Test cases for FastAPIGenerator"""

    def test_init(self):
        """Test FastAPIGenerator initialization"""
        generator = FastAPIGenerator()
        assert generator.file_manager is not None
        assert generator.templates is not None

    def test_python_type_filter(self):
        """Test Python type conversion filter"""
        generator = FastAPIGenerator()

        test_cases = [
            ("string", "str"),
            ("integer", "int"),
            ("boolean", "bool"),
            ("datetime", "datetime"),
            ("array", "List[Any]"),
            ("unknown", "str"),  # Default
        ]

        for input_type, expected in test_cases:
            result = generator._python_type_filter(input_type)
            assert result == expected

    @pytest.mark.asyncio
    async def test_generate(self, sample_api_spec, temp_dir):
        """Test FastAPI code generation"""
        generator = FastAPIGenerator()

        # Mock file operations
        generator.file_manager.write_file = AsyncMock()
        generator.file_manager.ensure_directory = AsyncMock()

        result = await generator.generate(sample_api_spec, temp_dir)

        # Check that expected files are in result
        expected_files = ["main.py", "requirements.txt", ".env.example"]
        for file_name in expected_files:
            assert file_name in result

        # Verify file manager was called
        assert generator.file_manager.write_file.call_count >= len(expected_files)

    @pytest.mark.asyncio
    async def test_generate_with_database(self, temp_dir):
        """Test generation with database requirements"""
        generator = FastAPIGenerator()

        # Create API spec with database
        api_spec = Mock()
        api_spec.name = "test_api"
        api_spec.description = "Test API"
        api_spec.database_required = True
        api_spec.auth_type = "jwt"
        api_spec.models = [{"name": "User", "fields": []}]
        api_spec.endpoints = []

        generator.file_manager.write_file = AsyncMock()
        generator.file_manager.ensure_directory = AsyncMock()

        result = await generator.generate(api_spec, temp_dir)

        # Should include database-related files
        assert "models.py" in result or any("model" in f for f in result.keys())


@pytest.mark.unit
class TestFlaskGenerator:
    """Test cases for FlaskGenerator"""

    def test_init(self):
        """Test FlaskGenerator initialization"""
        generator = FlaskGenerator()
        assert generator.file_manager is not None
        assert generator.templates is not None

    @pytest.mark.asyncio
    async def test_generate(self, sample_api_spec, temp_dir):
        """Test Flask code generation"""
        generator = FlaskGenerator()

        generator.file_manager.write_file = AsyncMock()
        generator.file_manager.ensure_directory = AsyncMock()

        result = await generator.generate(sample_api_spec, temp_dir)

        expected_files = ["app.py", "requirements.txt", "config.py"]
        for file_name in expected_files:
            assert file_name in result


@pytest.mark.unit
class TestGraphQLGenerator:
    """Test cases for GraphQLGenerator"""

    @pytest.mark.asyncio
    async def test_generate(self, sample_api_spec, temp_dir):
        """Test GraphQL code generation"""
        generator = GraphQLGenerator()

        generator.file_manager.write_file = AsyncMock()
        generator.file_manager.ensure_directory = AsyncMock()

        # Set API type to GraphQL
        sample_api_spec.api_type = ApiType.GRAPHQL

        result = await generator.generate(sample_api_spec, temp_dir)

        expected_files = ["app.py", "schema.py", "resolvers.py"]
        for file_name in expected_files:
            assert file_name in result


@pytest.mark.unit
class TestGRPCGenerator:
    """Test cases for GRPCGenerator"""

    @pytest.mark.asyncio
    async def test_generate(self, sample_api_spec, temp_dir):
        """Test gRPC code generation"""
        generator = GRPCGenerator()

        generator.file_manager.write_file = AsyncMock()
        generator.file_manager.ensure_directory = AsyncMock()

        sample_api_spec.api_type = ApiType.GRPC

        result = await generator.generate(sample_api_spec, temp_dir)

        expected_files = ["server.py", "client.py", f"{sample_api_spec.name}.proto"]
        for file_name in expected_files:
            assert file_name in result


@pytest.mark.unit
class TestWebSocketGenerator:
    """Test cases for WebSocketGenerator"""

    @pytest.mark.asyncio
    async def test_generate(self, sample_api_spec, temp_dir):
        """Test WebSocket code generation"""
        generator = WebSocketGenerator()

        generator.file_manager.write_file = AsyncMock()
        generator.file_manager.ensure_directory = AsyncMock()

        sample_api_spec.api_type = ApiType.WEBSOCKET

        result = await generator.generate(sample_api_spec, temp_dir)

        expected_files = ["server.py", "client_example.py"]
        for file_name in expected_files:
            assert file_name in result


@pytest.mark.unit
class TestCLIGenerator:
    """Test cases for CLIGenerator"""

    @pytest.mark.asyncio
    async def test_generate(self, sample_api_spec, temp_dir):
        """Test CLI code generation"""
        generator = CLIGenerator()

        generator.file_manager.write_file = AsyncMock()
        generator.file_manager.ensure_directory = AsyncMock()

        sample_api_spec.api_type = ApiType.CLI

        result = await generator.generate(sample_api_spec, temp_dir)

        expected_files = ["cli.py", "setup.py"]
        for file_name in expected_files:
            assert file_name in result


# tests/unit/test_validation.py

"""
Unit tests for validation utilities
"""

import pytest
from unittest.mock import patch

from text2api.utils.validation import (
    validate_api_name,
    validate_endpoint_path,
    validate_field_type,
    validate_http_method,
    validate_project_name,
    validate_api_spec,
    sanitize_filename,
    check_port_availability,
    suggest_alternative_port,
)


@pytest.mark.unit
class TestValidation:
    """Test cases for validation functions"""

    def test_validate_api_name(self):
        """Test API name validation"""
        valid_names = ["user_api", "ProductAPI", "api_v1", "simple"]
        invalid_names = ["", "123api", "api-name", "api name", "api.name"]

        for name in valid_names:
            assert validate_api_name(name) is True

        for name in invalid_names:
            assert validate_api_name(name) is False

    def test_validate_endpoint_path(self):
        """Test endpoint path validation"""
        valid_paths = ["/users", "/api/v1/users", "/users/{id}", "/users/{id}/posts"]
        invalid_paths = ["users", "", "api/users", "/users/{}", "/users/<id>"]

        for path in valid_paths:
            assert validate_endpoint_path(path) is True

        for path in invalid_paths:
            assert validate_endpoint_path(path) is False

    def test_validate_field_type(self):
        """Test field type validation"""
        valid_types = ["string", "integer", "float", "boolean", "datetime", "array"]
        invalid_types = ["str", "int", "varchar", "number", ""]

        for field_type in valid_types:
            assert validate_field_type(field_type) is True

        for field_type in invalid_types:
            assert validate_field_type(field_type) is False

    def test_validate_http_method(self):
        """Test HTTP method validation"""
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "get", "post"]
        invalid_methods = ["INVALID", "", "CONNECT", "TRACE"]

        for method in valid_methods:
            assert validate_http_method(method) is True

        for method in invalid_methods:
            assert validate_http_method(method) is False

    def test_validate_project_name(self):
        """Test project name validation"""
        valid_names = ["my_project", "project-1", "MyProject", "api_v2"]
        invalid_names = [
            "",
            "a",
            "very-long-name-" + "x" * 50,
            "123project",
            "project name",
        ]

        for name in valid_names:
            assert validate_project_name(name) is True

        for name in invalid_names:
            assert validate_project_name(name) is False

    def test_validate_api_spec(self):
        """Test API specification validation"""
        valid_spec = {
            "name": "test_api",
            "description": "Test API",
            "api_type": "rest",
            "endpoints": [{"path": "/users", "method": "GET", "name": "list_users"}],
        }

        result = validate_api_spec(valid_spec)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

        # Test invalid spec
        invalid_spec = {
            "name": "123invalid",
            "api_type": "invalid_type",
            "endpoints": "not_a_list",
        }

        result = validate_api_spec(invalid_spec)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        test_cases = [
            ("file<name>.txt", "filename.txt"),
            ("file name.txt", "file_name.txt"),
            ("file___name.txt", "file_name.txt"),
            ("___file___", "file"),
            ("", "unnamed"),
        ]

        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected

    def test_check_port_availability(self):
        """Test port availability check"""
        # Test with a port that should be available
        with patch("socket.socket") as mock_socket:
            mock_socket.return_value.__enter__.return_value.bind.return_value = None

            result = check_port_availability(12345)
            assert result is True

        # Test with occupied port
        with patch("socket.socket") as mock_socket:
            mock_socket.return_value.__enter__.return_value.bind.side_effect = OSError(
                "Port in use"
            )

            result = check_port_availability(80)
            assert result is False

    def test_suggest_alternative_port(self):
        """Test alternative port suggestion"""
        preferred_port = 8000

        # Mock port 8000 as unavailable, 8001 as available
        def mock_check_port(port):
            return port != 8000

        with patch(
            "text2api.utils.validation.check_port_availability",
            side_effect=mock_check_port,
        ):
            result = suggest_alternative_port(preferred_port)
            assert result == 8001
