"""
Analizator tekstu używający NLP do ekstraktowania informacji o API
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from langdetect import detect

from ..llm.ollama_client import OllamaClient
from ..llm.language_detector import LanguageDetector


class ApiType(Enum):
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    CLI = "cli"
    SSE = "sse"
    JSON_RPC = "json_rpc"


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class Field:
    name: str
    type: str
    required: bool = True
    description: str = ""
    default: Any = None
    validation: Optional[str] = None


@dataclass
class Endpoint:
    path: str
    method: HttpMethod
    name: str
    description: str
    parameters: List[Field]
    request_body: Optional[List[Field]] = None
    response_body: Optional[List[Field]] = None
    auth_required: bool = False


@dataclass
class ApiSpec:
    name: str
    description: str
    api_type: ApiType
    base_path: str
    endpoints: List[Endpoint]
    models: List[Dict[str, Any]]
    auth_type: Optional[str] = None
    database_required: bool = False
    external_apis: List[str] = None
    language: str = "en"
    framework: str = "fastapi"


class TextAnalyzer:
    """Główny analizator tekstu do generowania specyfikacji API"""

    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.language_detector = LanguageDetector()

        # Wzorce do rozpoznawania intencji
        self.patterns = {
            "crud_operations": [
                r"create|add|insert|new",
                r"read|get|fetch|retrieve|list|show",
                r"update|edit|modify|change",
                r"delete|remove|destroy",
            ],
            "api_types": {
                "rest": r"rest|restful|http|api|endpoint",
                "graphql": r"graphql|graph|query|mutation|subscription",
                "grpc": r"grpc|protobuf|protocol buffer|rpc",
                "websocket": r"websocket|real.?time|live|socket",
                "cli": r"cli|command|terminal|shell|script",
            },
            "data_entities": r"user|product|order|customer|item|post|article|comment|category",
            "authentication": r"auth|login|register|token|jwt|session|oauth",
            "database": r"database|db|sql|postgres|mysql|mongodb|store|persist",
            "external_apis": r"api|service|third.?party|external|integration",
        }

    async def analyze_text(self, text: str) -> ApiSpec:
        """Główna metoda analizy tekstu"""

        # Wykryj język
        language = self.language_detector.detect_language(text)

        # Użyj Ollama do szczegółowej analizy
        ollama_analysis = await self._analyze_with_ollama(text, language)

        # Połącz analizę wzorców z analizą LLM
        pattern_analysis = self._analyze_patterns(text)

        # Utwórz specyfikację API
        api_spec = self._create_api_spec(
            text, ollama_analysis, pattern_analysis, language
        )

        return api_spec

    async def _analyze_with_ollama(self, text: str, language: str) -> Dict[str, Any]:
        """Analiza z wykorzystaniem Ollama"""

        prompt = self._create_analysis_prompt(text, language)

        try:
            response = await self.ollama_client.generate(
                model="llama3.1:8b", prompt=prompt, format="json"
            )

            return json.loads(response)
        except Exception as e:
            print(f"Błąd analizy Ollama: {e}")
            return self._fallback_analysis(text)

    def _create_analysis_prompt(self, text: str, language: str) -> str:
        """Tworzy prompt dla Ollama"""

        lang_instructions = {
            "pl": "Analizuj poniższy tekst w języku polskim",
            "en": "Analyze the following text in English",
            "de": "Analysiere den folgenden Text auf Deutsch",
            "fr": "Analysez le texte suivant en français",
            "es": "Analiza el siguiente texto en español",
        }

        instruction = lang_instructions.get(language, lang_instructions["en"])

        return f"""
{instruction} i wygeneruj specyfikację API w formacie JSON:

Tekst: {text}

Zwróć JSON z następującymi polami:
{{
    "api_type": "rest|graphql|grpc|websocket|cli",
    "name": "nazwa_api",
    "description": "opis funkcjonalności",
    "framework": "fastapi|flask|graphene|grpc|click",
    "entities": ["lista", "głównych", "encji"],
    "endpoints": [
        {{
            "path": "/path",
            "method": "GET|POST|PUT|DELETE",
            "name": "nazwa_endpointu",
            "description": "opis",
            "parameters": [
                {{
                    "name": "param_name",
                    "type": "string|int|bool|float",
                    "required": true,
                    "description": "opis parametru"
                }}
            ],
            "request_body": [...],
            "response_body": [...]
        }}
    ],
    "auth_required": true|false,
    "database_required": true|false,
    "external_apis": ["lista", "zewnętrznych", "API"]
}}

Odpowiedz tylko kodem JSON, bez dodatkowych komentarzy.
"""

    def _analyze_patterns(self, text: str) -> Dict[str, Any]:
        """Analiza wzorców w tekście"""

        text_lower = text.lower()

        # Wykryj typ API
        api_type = ApiType.REST  # domyślny
        for api_name, pattern in self.patterns["api_types"].items():
            if re.search(pattern, text_lower):
                api_type = ApiType(api_name)
                break

        # Wykryj operacje CRUD
        crud_operations = []
        for i, pattern in enumerate(self.patterns["crud_operations"]):
            if re.search(pattern, text_lower):
                crud_operations.append(["create", "read", "update", "delete"][i])

        # Wykryj encje danych
        entities = []
        for match in re.finditer(self.patterns["data_entities"], text_lower):
            entities.append(match.group())

        # Wykryj potrzebę autoryzacji
        auth_required = bool(re.search(self.patterns["authentication"], text_lower))

        # Wykryj potrzebę bazy danych
        database_required = bool(re.search(self.patterns["database"], text_lower))

        return {
            "api_type": api_type,
            "crud_operations": crud_operations,
            "entities": list(set(entities)),
            "auth_required": auth_required,
            "database_required": database_required,
        }

    def _create_api_spec(
        self,
        text: str,
        ollama_analysis: Dict[str, Any],
        pattern_analysis: Dict[str, Any],
        language: str,
    ) -> ApiSpec:
        """Tworzy ostateczną specyfikację API"""

        # Połącz wyniki analiz
        api_type = ApiType(
            ollama_analysis.get("api_type", pattern_analysis["api_type"].value)
        )

        name = ollama_analysis.get("name", self._extract_name_from_text(text))
        description = ollama_analysis.get("description", "Generated API")

        # Wybierz framework na podstawie typu API
        framework_mapping = {
            ApiType.REST: ollama_analysis.get("framework", "fastapi"),
            ApiType.GRAPHQL: "graphene",
            ApiType.GRPC: "grpc",
            ApiType.WEBSOCKET: "websockets",
            ApiType.CLI: "click",
        }

        framework = framework_mapping.get(api_type, "fastapi")

        # Utwórz endpointy
        endpoints = self._create_endpoints(
            ollama_analysis.get("endpoints", []),
            pattern_analysis["entities"],
            pattern_analysis["crud_operations"],
        )

        # Utwórz modele
        models = self._create_models(
            pattern_analysis["entities"], ollama_analysis.get("entities", [])
        )

        return ApiSpec(
            name=name,
            description=description,
            api_type=api_type,
            base_path="/api/v1",
            endpoints=endpoints,
            models=models,
            auth_type="jwt" if pattern_analysis["auth_required"] else None,
            database_required=pattern_analysis["database_required"],
            external_apis=ollama_analysis.get("external_apis", []),
            language=language,
            framework=framework,
        )

    def _create_endpoints(
        self, ollama_endpoints: List[Dict], entities: List[str], crud_ops: List[str]
    ) -> List[Endpoint]:
        """Tworzy listę endpointów"""

        endpoints = []

        # Najpierw użyj endpointów z Ollama
        for ep_data in ollama_endpoints:
            endpoint = Endpoint(
                path=ep_data.get("path", "/"),
                method=HttpMethod(ep_data.get("method", "GET")),
                name=ep_data.get("name", "unnamed"),
                description=ep_data.get("description", ""),
                parameters=[
                    Field(
                        name=p["name"],
                        type=p["type"],
                        required=p.get("required", True),
                        description=p.get("description", ""),
                    )
                    for p in ep_data.get("parameters", [])
                ],
                request_body=[
                    Field(
                        name=f["name"],
                        type=f["type"],
                        required=f.get("required", True),
                        description=f.get("description", ""),
                    )
                    for f in ep_data.get("request_body", [])
                ]
                if ep_data.get("request_body")
                else None,
                response_body=[
                    Field(
                        name=f["name"],
                        type=f["type"],
                        required=f.get("required", True),
                        description=f.get("description", ""),
                    )
                    for f in ep_data.get("response_body", [])
                ]
                if ep_data.get("response_body")
                else None,
            )
            endpoints.append(endpoint)

        # Jeśli brak endpointów z Ollama, utwórz na podstawie wzorców
        if not endpoints and entities:
            endpoints = self._generate_crud_endpoints(entities, crud_ops)

        return endpoints

    def _generate_crud_endpoints(
        self, entities: List[str], crud_ops: List[str]
    ) -> List[Endpoint]:
        """Generuje standardowe endpointy CRUD"""

        endpoints = []

        for entity in entities:
            entity_singular = entity.rstrip("s")  # prosta singularizacja
            entity_path = f"/{entity}"

            if "create" in crud_ops:
                endpoints.append(
                    Endpoint(
                        path=entity_path,
                        method=HttpMethod.POST,
                        name=f"create_{entity_singular}",
                        description=f"Create a new {entity_singular}",
                        parameters=[],
                        request_body=[
                            Field(
                                name="name",
                                type="string",
                                description=f"{entity_singular} name",
                            ),
                            Field(name="description", type="string", required=False),
                        ],
                        response_body=[
                            Field(name="id", type="integer"),
                            Field(name="name", type="string"),
                            Field(name="created_at", type="datetime"),
                        ],
                    )
                )

            if "read" in crud_ops:
                # Lista
                endpoints.append(
                    Endpoint(
                        path=entity_path,
                        method=HttpMethod.GET,
                        name=f"list_{entity}",
                        description=f"Get list of {entity}",
                        parameters=[
                            Field(
                                name="limit", type="integer", required=False, default=10
                            ),
                            Field(
                                name="offset", type="integer", required=False, default=0
                            ),
                        ],
                        response_body=[
                            Field(name="items", type="array"),
                            Field(name="total", type="integer"),
                        ],
                    )
                )

                # Pojedynczy element
                endpoints.append(
                    Endpoint(
                        path=f"{entity_path}/{{id}}",
                        method=HttpMethod.GET,
                        name=f"get_{entity_singular}",
                        description=f"Get {entity_singular} by ID",
                        parameters=[
                            Field(
                                name="id",
                                type="integer",
                                description=f"{entity_singular} ID",
                            )
                        ],
                        response_body=[
                            Field(name="id", type="integer"),
                            Field(name="name", type="string"),
                        ],
                    )
                )

            if "update" in crud_ops:
                endpoints.append(
                    Endpoint(
                        path=f"{entity_path}/{{id}}",
                        method=HttpMethod.PUT,
                        name=f"update_{entity_singular}",
                        description=f"Update {entity_singular}",
                        parameters=[
                            Field(
                                name="id",
                                type="integer",
                                description=f"{entity_singular} ID",
                            )
                        ],
                        request_body=[
                            Field(name="name", type="string", required=False),
                            Field(name="description", type="string", required=False),
                        ],
                    )
                )

            if "delete" in crud_ops:
                endpoints.append(
                    Endpoint(
                        path=f"{entity_path}/{{id}}",
                        method=HttpMethod.DELETE,
                        name=f"delete_{entity_singular}",
                        description=f"Delete {entity_singular}",
                        parameters=[
                            Field(
                                name="id",
                                type="integer",
                                description=f"{entity_singular} ID",
                            )
                        ],
                    )
                )

        return endpoints

    def _create_models(
        self, pattern_entities: List[str], ollama_entities: List[str]
    ) -> List[Dict[str, Any]]:
        """Tworzy modele danych"""

        all_entities = list(set(pattern_entities + ollama_entities))
        models = []

        for entity in all_entities:
            entity_singular = entity.rstrip("s")

            model = {
                "name": entity_singular.capitalize(),
                "fields": [
                    {"name": "id", "type": "integer", "primary_key": True},
                    {"name": "name", "type": "string", "required": True},
                    {"name": "description", "type": "string", "required": False},
                    {"name": "created_at", "type": "datetime", "auto_now_add": True},
                    {"name": "updated_at", "type": "datetime", "auto_now": True},
                ],
            }
            models.append(model)

        return models

    def _extract_name_from_text(self, text: str) -> str:
        """Ekstraktuje nazwę API z tekstu"""

        # Szukaj nazwy w pierwszym zdaniu
        first_sentence = text.split(".")[0]

        # Usuń słowa pomocnicze
        words = first_sentence.lower().split()
        stop_words = {"api", "for", "to", "the", "a", "an", "create", "build", "make"}

        name_words = [w for w in words if w not in stop_words and w.isalpha()]

        if name_words:
            return "_".join(name_words[:3])  # maksymalnie 3 słowa

        return "generated_api"

    def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback analiza gdy Ollama nie działa"""

        return {
            "api_type": "rest",
            "name": self._extract_name_from_text(text),
            "description": "Generated API from text description",
            "framework": "fastapi",
            "entities": ["item"],
            "endpoints": [],
            "auth_required": False,
            "database_required": True,
            "external_apis": [],
        }
