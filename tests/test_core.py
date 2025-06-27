import pytest
from text2api.core import (
    TextAnalyzer,
    ApiSpec,
    Endpoint,
    Field,
    APIGenerator,
    HttpMethod,
)


def test_text_analyzer():
    analyzer = TextAnalyzer()
    spec = analyzer.analyze("Create a simple REST API for managing books")
    assert isinstance(spec, ApiSpec)
    assert len(spec.endpoints) > 0


def test_api_spec():
    spec = ApiSpec(
        name="Test API",
        description="Test API description",
        endpoints=[
            Endpoint(path="/test", method=HttpMethod.GET, description="Test endpoint")
        ],
    )
    assert spec.name == "Test API"
    assert len(spec.endpoints) == 1


def test_endpoint():
    endpoint = Endpoint(
        path="/test", method=HttpMethod.GET, description="Test endpoint"
    )
    assert endpoint.path == "/test"
    assert endpoint.method == HttpMethod.GET


def test_field():
    field = Field(name="test_field", type="string", description="Test field")
    assert field.name == "test_field"
    assert field.type == "string"
