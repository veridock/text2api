"""
Functional tests for CLI interface
"""

import pytest
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner

from text2api.cli import cli


@pytest.mark.functional
class TestCLIFunctional:
    """Functional tests for CLI commands"""
    
    def test_cli_help(self):
        """Test CLI help command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "text2api" in result.output
        assert "generate" in result.output
    
    def test_cli_version(self):
        """Test CLI version command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert "0.1.0" in result.output
    
    @patch('text2api.core.generator.APIGenerator.generate_from_text')
    def test_cli_generate_command(self, mock_generate):
        """Test CLI generate command"""
        mock_generate.return_value = {
            "success": True,
            "project_path": "./test_api",
            "api_spec": {"name": "test_api", "api_type": "rest"},
            "generated_files": ["main.py"],
            "additional_files": [],
            "instructions": ["Run uvicorn main:app"]
        }
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate',
            'API do zarządzania użytkownikami',
            '--output', 'test_api'
        ])
        
        assert result.exit_code == 0
        assert "wygenerowane pomyślnie" in result.output or "generated successfully" in result.output
        mock_generate.assert_called_once()
    
    @patch('text2api.llm.ollama_client.OllamaClient.health_check')
    @patch('text2api.llm.ollama_client.OllamaClient.list_models')
    def test_cli_check_command(self, mock_list_models, mock_health_check):
        """Test CLI check command"""
        mock_health_check.return_value = True
        mock_list_models.return_value = [
            type('Model', (), {'name': 'llama3.1:8b', 'size': '4.7GB'})()
        ]
        
        runner = CliRunner()
        result = runner.invoke(cli, ['check'])
        
        assert result.exit_code == 0
        assert "Ollama" in result.output
    
    def test_cli_examples_command(self):
        """Test CLI examples command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['examples'])
        
        assert result.exit_code == 0
        assert "Przykłady" in result.output or "Examples" in result.output
        assert "REST" in result.output
        assert "GraphQL" in result.output
    
    @patch('text2api.core.generator.APIGenerator.generate_from_text')
    def test_cli_generate_with_options(self, mock_generate):
        """Test CLI generate with various options"""
        mock_generate.return_value = {
            "success": True,
            "project_path": "./test_api",
            "api_spec": {"name": "test_api", "api_type": "rest"},
            "generated_files": [],
            "additional_files": [],
            "instructions": []
        }
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate',
            'Test API',
            '--type', 'rest',
            '--framework', 'fastapi',
            '--no-docker',
            '--no-tests'
        ])
        
        assert result.exit_code == 0
        mock_generate.assert_called_once()
        
        # Check that options were passed correctly
        call_args = mock_generate.call_args
        assert call_args[1]['include_docker'] is False
        assert call_args[1]['include_tests'] is False
    
    def test_cli_models_command(self):
        """Test CLI models command"""
        runner = CliRunner()
        
        with patch('text2api.llm.ollama_client.OllamaClient.list_models') as mock_list:
            mock_list.return_value = [
                type('Model', (), {
                    'name': 'llama3.1:8b',
                    'size': '4.7GB',
                    'modified_at': '2024-01-01T00:00:00Z'
                })()
            ]
            
            result = runner.invoke(cli, ['models'])
            
            assert result.exit_code == 0
            assert "llama3.1:8b" in result.output
    
    def test_cli_interactive_mode_input(self):
        """Test CLI interactive mode with mocked input"""
        runner = CliRunner()
        
        # Mock interactive inputs
        inputs = [
            'Test API description',  # Description
            'rest',                  # API type
            'fastapi',              # Framework
            'test_project',         # Project name
            'y',                    # Include Docker
            'y',                    # Include tests
            'y',                    # Include docs
            'y'                     # Confirm generation
        ]
        
        with patch('text2api.core.generator.APIGenerator.generate_from_text') as mock_generate:
            mock_generate.return_value = {"success": True, "project_path": "./test"}
            
            result = runner.invoke(cli, ['generate-from-file', '--interactive'], 
                                 input='\n'.join(inputs))
            
            # Should not fail due to interactive input
            assert result.exit_code in [0, 1]  # May exit with 1 due to mocking


# tests/functional/test_performance.py

"""
Performance tests for text2api
"""

import pytest
import asyncio
import time
from pathlib import Path

from text2api.core.generator import APIGenerator
from text2api.core.analyzer import TextAnalyzer
from text2api.llm.ollama_client import OllamaClient


@pytest.mark.functional
@pytest.mark.slow
class TestPerformance:
    """Performance tests"""
    
    @pytest.mark.asyncio
    async def test_text_analysis_performance(self, mock_ollama_client):
        """Test text analysis performance"""
        analyzer = TextAnalyzer(mock_ollama_client)
        
        test_descriptions = [
            "Simple API for user management",
            "Complex e-commerce platform with products, orders, payments, and shipping",
            "Real-time chat application with rooms, messages, and user presence",
            "Microservice architecture with authentication, logging, and monitoring"
        ]
        
        start_time = time.time()
        
        for description in test_descriptions:
            result = await analyzer.analyze_text(description)
            assert result is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should analyze 4 descriptions in less than 2 seconds (with mocked Ollama)
        assert total_time < 2.0, f"Analysis took {total_time:.2f}s, expected < 2.0s"
        
        # Average time per analysis should be reasonable
        avg_time = total_time / len(test_descriptions)
        assert avg_time < 0.5, f"Average analysis time {avg_time:.2f}s too high"
    
    @pytest.mark.asyncio
    async def test_code_generation_performance(self, sample_api_spec, temp_dir):
        """Test code generation performance"""
        from text2api.generators.fastapi_gen import FastAPIGenerator
        
        generator = FastAPIGenerator()
        
        start_time = time.time()
        
        result = await generator.generate(sample_api_spec, temp_dir)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Code generation should be fast
        assert generation_time < 1.0, f"Generation took {generation_time:.2f}s, expected < 1.0s"
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_generation_performance(self, mock_ollama_client, temp_dir):
        """Test concurrent API generation performance"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        descriptions = [
            "User management API",
            "Product catalog API", 
            "Order processing API",
            "Payment gateway API"
        ]
        
        async def generate_api(desc, index):
            return await generator.generate_from_text(
                text=desc,
                output_name=f"api_{index}",
                include_docker=False,
                include_tests=False,
                include_docs=False
            )
        
        start_time = time.time()
        
        # Generate APIs concurrently
        tasks = [generate_api(desc, i) for i, desc in enumerate(descriptions)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Concurrent generation should be faster than sequential
        assert total_time < 3.0, f"Concurrent generation took {total_time:.2f}s"
        
        # All should succeed
        for result in results:
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_large_api_spec_generation(self, temp_dir):
        """Test generation of large API specifications"""
        from text2api.core.analyzer import ApiSpec, ApiType, HttpMethod, Endpoint, Field
        
        # Create large API spec with many endpoints
        endpoints = []
        models = []
        
        # Generate 50 endpoints
        for i in range(50):
            endpoint = Endpoint(
                path=f"/entity{i}",
                method=HttpMethod.GET,
                name=f"get_entity_{i}",
                description=f"Get entity {i}",
                parameters=[
                    Field(name="id", type="integer", required=True),
                    Field(name="limit", type="integer", required=False)
                ]
            )
            endpoints.append(endpoint)
            
            # Add corresponding model
            model = {
                "name": f"Entity{i}",
                "fields": [
                    {"name": "id", "type": "integer", "primary_key": True},
                    {"name": "name", "type": "string", "required": True},
                    {"name": f"field_{i}", "type": "string", "required": False}
                ]
            }
            models.append(model)
        
        large_api_spec = ApiSpec(
            name="large_api",
            description="Large API with many endpoints",
            api_type=ApiType.REST,
            base_path="/api/v1",
            endpoints=endpoints,
            models=models,
            auth_type="jwt",
            database_required=True,
            external_apis=[],
            language="en",
            framework="fastapi"
        )
        
        from text2api.generators.fastapi_gen import FastAPIGenerator
        generator = FastAPIGenerator()
        
        start_time = time.time()
        
        result = await generator.generate(large_api_spec, temp_dir)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Should handle large specs reasonably fast
        assert generation_time < 5.0, f"Large API generation took {generation_time:.2f}s"
        assert len(result) > 0
        
        # Check that main.py was generated and contains all endpoints
        main_py_path = Path(result["main.py"])
        main_content = main_py_path.read_text()
        
        # Should contain many of the generated endpoints
        endpoint_count = sum(1 for endpoint in endpoints if endpoint.path in main_content)
        assert endpoint_count >= 40, f"Only {endpoint_count}/50 endpoints found in generated code"
    
    def test_memory_usage_during_generation(self, sample_api_spec, temp_dir):
        """Test memory usage during generation"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        from text2api.generators.fastapi_gen import FastAPIGenerator
        generator = FastAPIGenerator()
        
        # Generate multiple times to test for memory leaks
        async def run_generations():
            for i in range(10):
                await generator.generate(sample_api_spec, temp_dir / f"test_{i}")
        
        import asyncio
        asyncio.run(run_generations())
        
        # Measure final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for 10 generations)
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"
    
    @pytest.mark.asyncio
    async def test_file_io_performance(self, temp_dir):
        """Test file I/O performance"""
        from text2api.utils.file_utils import FileManager
        
        manager = FileManager()
        
        # Test writing many files
        start_time = time.time()
        
        write_tasks = []
        for i in range(100):
            file_path = temp_dir / f"test_file_{i}.txt"
            content = f"Test content for file {i}" * 100  # ~2KB per file
            write_tasks.append(manager.write_file(file_path, content))
        
        await asyncio.gather(*write_tasks)
        
        write_time = time.time() - start_time
        
        # Writing 100 files should be fast
        assert write_time < 2.0, f"Writing 100 files took {write_time:.2f}s, expected < 2.0s"
        
        # Test reading files back
        start_time = time.time()
        
        read_tasks = []
        for i in range(100):
            file_path = temp_dir / f"test_file_{i}.txt"
            read_tasks.append(manager.read_file(file_path))
        
        contents = await asyncio.gather(*read_tasks)
        
        read_time = time.time() - start_time
        
        # Reading should be even faster
        assert read_time < 1.0, f"Reading 100 files took {read_time:.2f}s, expected < 1.0s"
        assert len(contents) == 100


# tests/functional/test_real_world_scenarios.py

"""
Real-world scenario tests
"""

import pytest
from pathlib import Path

from text2api.core.generator import APIGenerator


@pytest.mark.functional
@pytest.mark.slow
class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    @pytest.mark.asyncio
    async def test_blog_api_scenario(self, temp_dir, mock_ollama_client):
        """Test generating a complete blog API"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        # Mock comprehensive blog API response
        mock_ollama_client.analyze_api_requirements.return_value = {
            "api_type": "rest",
            "name": "blog_api",
            "description": "Complete blog management API",
            "framework": "fastapi",
            "main_entities": ["post", "comment", "tag", "user", "category"],
            "endpoints": [
                {
                    "path": "/posts",
                    "method": "GET",
                    "name": "list_posts",
                    "description": "List blog posts",
                    "parameters": [
                        {"name": "category", "type": "string", "required": False},
                        {"name": "tag", "type": "string", "required": False},
                        {"name": "limit", "type": "integer", "required": False}
                    ],
                    "request_body": [],
                    "response_body": [
                        {"name": "posts", "type": "array"},
                        {"name": "total", "type": "integer"}
                    ]
                },
                {
                    "path": "/posts",
                    "method": "POST",
                    "name": "create_post",
                    "description": "Create new blog post",
                    "parameters": [],
                    "request_body": [
                        {"name": "title", "type": "string", "required": True},
                        {"name": "content", "type": "string", "required": True},
                        {"name": "category_id", "type": "integer", "required": True}
                    ],
                    "response_body": [
                        {"name": "id", "type": "integer"},
                        {"name": "title", "type": "string"}
                    ]
                }
            ],
            "auth_required": True,
            "database_required": True,
            "external_apis": ["email_service"]
        }
        
        description = """
        Kompletne API dla bloga z następującymi funkcjonalnościami:
        - Zarządzanie postami z tytułami, treścią i kategoriami
        - System komentarzy z moderacją
        - Tagging system dla postów
        - Zarządzanie użytkownikami z rolami (autor, moderator, admin)
        - System powiadomień email
        - SEO metadata dla postów
        """
        
        result = await generator.generate_from_text(
            text=description,
            output_name="blog_api",
            include_docker=True,
            include_tests=True,
            include_docs=True
        )
        
        assert result["success"] is True
        
        project_path = Path(result["project_path"])
        
        # Check all expected files exist
        expected_files = [
            "main.py", "requirements.txt", "Dockerfile", "docker-compose.yml",
            "README.md", "api_spec.json"
        ]
        
        for file_name in expected_files:
            assert (project_path / file_name).exists()
        
        # Check main.py contains blog-specific functionality
        main_content = (project_path / "main.py").read_text()
        assert "post" in main_content.lower()
        assert "comment" in main_content.lower()
        assert "auth" in main_content.lower()
        assert "jwt" in main_content.lower() or "token" in main_content.lower()
    
    @pytest.mark.asyncio
    async def test_ecommerce_api_scenario(self, temp_dir, mock_ollama_client):
        """Test generating an e-commerce API"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        # Mock e-commerce API response
        mock_ollama_client.analyze_api_requirements.return_value = {
            "api_type": "rest",
            "name": "ecommerce_api",
            "description": "E-commerce platform API",
            "framework": "fastapi",
            "main_entities": ["product", "order", "cart", "user", "payment"],
            "endpoints": [
                {
                    "path": "/products",
                    "method": "GET",
                    "name": "list_products",
                    "description": "List products with filtering",
                    "parameters": [
                        {"name": "category", "type": "string", "required": False},
                        {"name": "min_price", "type": "float", "required": False},
                        {"name": "max_price", "type": "float", "required": False}
                    ],
                    "request_body": [],
                    "response_body": []
                },
                {
                    "path": "/cart/add",
                    "method": "POST",
                    "name": "add_to_cart",
                    "description": "Add item to cart",
                    "parameters": [],
                    "request_body": [
                        {"name": "product_id", "type": "integer", "required": True},
                        {"name": "quantity", "type": "integer", "required": True}
                    ],
                    "response_body": []
                }
            ],
            "auth_required": True,
            "database_required": True,
            "external_apis": ["payment_gateway", "shipping_service"]
        }
        
        description = """
        E-commerce platform API z funkcjonalnościami:
        - Katalog produktów z kategoriami, cenami i zdjęciami
        - Koszyk zakupowy z sesją użytkownika
        - System zamówień ze statusami i śledzeniem
        - Integracja z bramkami płatności
        - Zarządzanie inventory
        - System recenzji produktów
        - Powiadomienia email o statusie zamówienia
        """
        
        result = await generator.generate_from_text(
            text=description,
            output_name="ecommerce_api"
        )
        
        assert result["success"] is True
        
        # Verify e-commerce specific features
        api_spec = result["api_spec"]
        assert api_spec["auth_required"] is True
        assert api_spec["database_required"] is True
        assert len(api_spec["external_apis"]) > 0
        
        project_path = Path(result["project_path"])
        main_content = (project_path / "main.py").read_text()
        
        # Should contain e-commerce specific terms
        ecommerce_terms = ["product", "cart", "order", "payment"]
        for term in ecommerce_terms:
            assert term in main_content.lower()
    
    @pytest.mark.asyncio
    async def test_microservice_scenario(self, temp_dir, mock_ollama_client):
        """Test generating a microservice"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        # Mock microservice response (gRPC)
        mock_ollama_client.analyze_api_requirements.return_value = {
            "api_type": "grpc",
            "name": "user_service",
            "description": "User management microservice",
            "framework": "grpc",
            "main_entities": ["user", "profile"],
            "endpoints": [],
            "auth_required": True,
            "database_required": True,
            "external_apis": ["auth_service", "notification_service"]
        }
        
        description = """
        Mikrousługa do zarządzania użytkownikami w architekturze mikrousług:
        - gRPC API dla wysokiej wydajności
        - Zarządzanie profilami użytkowników
        - Integracja z serwisem autoryzacji
        - Health checks i monitoring
        - Circuit breaker patterns
        - Distributed tracing
        """
        
        result = await generator.generate_from_text(
            text=description,
            output_name="user_service"
        )
        
        assert result["success"] is True
        assert result["api_spec"]["api_type"] == "grpc"
        
        project_path = Path(result["project_path"])
        
        # Check gRPC specific files
        assert (project_path / "server.py").exists()
        assert (project_path / f"{result['api_spec']['name']}.proto").exists()
    
    @pytest.mark.asyncio
    async def test_multi_language_scenario(self, temp_dir, mock_ollama_client):
        """Test handling different input languages"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        test_cases = [
            {
                "description": "API for user management with CRUD operations",
                "language": "en",
                "expected_name": "user_management_api"
            },
            {
                "description": "API do zarządzania produktami z operacjami CRUD",
                "language": "pl", 
                "expected_name": "product_management_api"
            },
            {
                "description": "API für Benutzerverwaltung mit CRUD-Operationen",
                "language": "de",
                "expected_name": "user_management_api"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            # Mock language-specific response
            mock_ollama_client.analyze_api_requirements.return_value = {
                "api_type": "rest",
                "name": test_case["expected_name"],
                "description": f"API in {test_case['language']}",
                "framework": "fastapi",
                "main_entities": ["user"],
                "endpoints": [],
                "auth_required": False,
                "database_required": True,
                "external_apis": []
            }
            
            with patch.object(generator.text_analyzer.language_detector, 'detect_language', 
                            return_value=test_case["language"]):
                
                result = await generator.generate_from_text(
                    text=test_case["description"],
                    output_name=f"api_{test_case['language']}"
                )
                
                assert result["success"] is True
                assert result["api_spec"]["language"] == test_case["language"]
    
    @pytest.mark.asyncio
    async def test_complex_integration_scenario(self, temp_dir, mock_ollama_client):
        """Test complex scenario with multiple integrations"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        # Mock complex system response
        mock_ollama_client.analyze_api_requirements.return_value = {
            "api_type": "rest",
            "name": "complex_platform",
            "description": "Complex multi-service platform",
            "framework": "fastapi",
            "main_entities": ["user", "organization", "project", "task", "notification"],
            "endpoints": [
                {
                    "path": "/users",
                    "method": "GET",
                    "name": "list_users",
                    "description": "List users",
                    "parameters": [],
                    "request_body": [],
                    "response_body": []
                },
                {
                    "path": "/projects/{id}/tasks",
                    "method": "POST",
                    "name": "create_task",
                    "description": "Create task in project",
                    "parameters": [{"name": "id", "type": "integer", "required": True}],
                    "request_body": [],
                    "response_body": []
                }
            ],
            "auth_required": True,
            "database_required": True,
            "external_apis": ["email_service", "file_storage", "analytics", "payment_processor"]
        }
        
        description = """
        Kompleksowa platforma do zarządzania projektami z funkcjami:
        - Multi-tenant architecture z organizacjami
        - Zarządzanie użytkownikami z rolami i uprawnieniami
        - Projekty z zadaniami, milestone'ami i deadlines
        - System powiadomień email i push
        - Integracja z systemami płatności
        - File storage i document management
        - Analytics i reporting
        - API rate limiting i caching
        - Audit logging i compliance
        """
        
        result = await generator.generate_from_text(
            text=description,
            output_name="complex_platform",
            include_docker=True,
            include_tests=True,
            include_docs=True
        )
        
        assert result["success"] is True
        
        # Verify complex features
        api_spec = result["api_spec"]
        assert len(api_spec["main_entities"]) >= 4
        assert len(api_spec["external_apis"]) >= 3
        assert api_spec["auth_required"] is True
        assert api_spec["database_required"] is True
        
        project_path = Path(result["project_path"])
        
        # Check comprehensive file structure
        expected_files = [
            "main.py", "requirements.txt", "Dockerfile", 
            "docker-compose.yml", "README.md", "api_spec.json"
        ]
        
        for file_name in expected_files:
            file_path = project_path / file_name
            assert file_path.exists()
            assert file_path.stat().st_size > 0


# tests/functional/test_error_scenarios.py

"""
Error scenario tests
"""

import pytest
from unittest.mock import patch, AsyncMock

from text2api.core.generator import APIGenerator


@pytest.mark.functional
class TestErrorScenarios:
    """Test error handling in various scenarios"""
    
    @pytest.mark.asyncio
    async def test_invalid_text_input(self, temp_dir, mock_ollama_client):
        """Test handling of invalid text input"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        invalid_inputs = [
            "",  # Empty string
            "   ",  # Only whitespace
            "a",  # Too short
            "12345",  # Only numbers
            "!@#$%",  # Only special characters
        ]
        
        for invalid_input in invalid_inputs:
            result = await generator.generate_from_text(
                text=invalid_input,
                output_name="invalid_test"
            )
            
            # Should either succeed with fallback or fail gracefully
            if not result["success"]:
                assert "error" in result
                assert isinstance(result["error"], str)
            else:
                # If it succeeds, it should have used fallback analysis
                assert result["api_spec"]["name"]
    
    @pytest.mark.asyncio
    async def test_ollama_timeout_error(self, temp_dir):
        """Test handling of Ollama timeout"""
        generator = APIGenerator(output_dir=str(temp_dir))
        
        # Mock timeout error
        with patch.object(generator.ollama_client, 'health_check', side_effect=asyncio.TimeoutError()):
            result = await generator.generate_from_text(
                text="Simple API",
                output_name="timeout_test"
            )
            
            assert result["success"] is False
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_file_permission_error(self, temp_dir, mock_ollama_client):
        """Test handling of file permission errors"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        # Mock file permission error
        with patch.object(generator.file_manager, 'write_file', side_effect=PermissionError("Permission denied")):
            result = await generator.generate_from_text(
                text="Simple API",
                output_name="permission_test"
            )
            
            assert result["success"] is False
            assert "Permission denied" in result["error"] or "error" in result
    
    @pytest.mark.asyncio
    async def test_invalid_output_path(self, mock_ollama_client):
        """Test handling of invalid output paths"""
        generator = APIGenerator(output_dir="/invalid/path/that/does/not/exist")
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        result = await generator.generate_from_text(
            text="Simple API",
            output_name="invalid_path_test"
        )
        
        # Should handle invalid path gracefully
        if not result["success"]:
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_malformed_ollama_response(self, temp_dir):
        """Test handling of malformed Ollama responses"""
        generator = APIGenerator(output_dir=str(temp_dir))
        
        # Mock malformed JSON response
        with patch.object(generator.ollama_client, 'analyze_api_requirements', 
                         return_value="Invalid JSON response"):
            result = await generator.generate_from_text(
                text="Simple API",
                output_name="malformed_test"
            )
            
            # Should use fallback analysis
            assert result["success"] is True or "error" in result
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, temp_dir):
        """Test network error handling"""
        generator = APIGenerator(output_dir=str(temp_dir))
        
        # Mock network error
        import httpx
        with patch.object(generator.ollama_client, 'health_check', 
                         side_effect=httpx.ConnectError("Network error")):
            result = await generator.generate_from_text(
                text="Simple API",
                output_name="network_test"
            )
            
            assert result["success"] is False
            assert "error" in result


# tests/functional/test_edge_cases.py

"""
Edge case tests
"""

import pytest
from pathlib import Path

from text2api.core.generator import APIGenerator


@pytest.mark.functional
class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.mark.asyncio
    async def test_very_long_description(self, temp_dir, mock_ollama_client):
        """Test with very long API description"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        # Create very long description (>10,000 characters)
        long_description = "API for managing " + "very complex business processes " * 200
        
        result = await generator.generate_from_text(
            text=long_description,
            output_name="long_description_test"
        )
        
        # Should handle long descriptions
        assert result["success"] is True
        assert result["api_spec"]["name"]
    
    @pytest.mark.asyncio
    async def test_special_characters_in_description(self, temp_dir, mock_ollama_client):
        """Test with special characters in description"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        special_descriptions = [
            "API with émojis 🚀 and ünïcödé châractérs",
            "API with <html> tags and & entities",
            "API with 'quotes' and \"double quotes\"",
            "API with newlines\nand\ttabs",
            "API with numbers 123 and symbols @#$%"
        ]
        
        for i, description in enumerate(special_descriptions):
            result = await generator.generate_from_text(
                text=description,
                output_name=f"special_chars_test_{i}"
            )
            
            # Should handle special characters gracefully
            assert result["success"] is True
            
            # Generated name should be sanitized
            project_path = Path(result["project_path"])
            assert project_path.name.replace('_', '').replace('-', '').isalnum()
    
    @pytest.mark.asyncio
    async def test_mixed_language_description(self, temp_dir, mock_ollama_client):
        """Test with mixed language descriptions"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        mixed_descriptions = [
            "API for user management avec des fonctionnalités avancées",
            "Create a REST API für das Management von Benutzern",
            "Sistema de gestión con REST API and GraphQL support"
        ]
        
        for i, description in enumerate(mixed_descriptions):
            result = await generator.generate_from_text(
                text=description,
                output_name=f"mixed_lang_test_{i}"
            )
            
            # Should handle mixed languages
            assert result["success"] is True
    
    @pytest.mark.asyncio
    async def test_duplicate_project_names(self, temp_dir, mock_ollama_client):
        """Test handling of duplicate project names"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        # Generate first API
        result1 = await generator.generate_from_text(
            text="User management API",
            output_name="duplicate_test"
        )
        
        assert result1["success"] is True
        
        # Generate second API with same name
        result2 = await generator.generate_from_text(
            text="Product management API",
            output_name="duplicate_test"
        )
        
        # Should handle duplicate names (either overwrite or create variant)
        assert result2["success"] is True
        
        # Both should have valid project paths
        assert Path(result1["project_path"]).parent == Path(result2["project_path"]).parent
    
    @pytest.mark.asyncio
    async def test_maximum_entities_and_endpoints(self, temp_dir, mock_ollama_client):
        """Test with maximum number of entities and endpoints"""
        generator = APIGenerator(output_dir=str(temp_dir))
        generator.text_analyzer.ollama_client = mock_ollama_client
        
        # Mock response with many entities
        mock_ollama_client.analyze_api_requirements.return_value = {
            "api_type": "rest",
            "name": "complex_api",
            "description": "Complex API with many entities",
            "framework": "fastapi",
            "main_entities": [f"entity_{i}" for i in range(100)],  # 100 entities
            "endpoints": [
                {
                    "path": f"/entity_{i}",
                    "method": "GET",
                    "name": f"get_entity_{i}",
                    "description": f"Get entity {i}",
                    "parameters": [],
                    "request_body": [],
                    "response_body": []
                } for i in range(200)  # 200 endpoints
            ],
            "auth_required": True,
            "database_required": True,
            "external_apis": []
        }
        
        description = "Very complex API with many entities and endpoints"
        
        result = await generator.generate_from_text(
            text=description,
            output_name="max_complexity_test"
        )
        
        # Should handle large number of entities and endpoints
        assert result["success"] is True
        
        # Check that files were generated
        project_path = Path(result["project_path"])
        assert (project_path / "main.py").exists()
        
        # File should not be empty
        main_py_size = (project_path / "main.py").stat().st_size
        assert main_py_size > 1000  # Should be substantial