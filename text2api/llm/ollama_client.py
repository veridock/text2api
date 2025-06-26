"""
Klient do komunikacji z Ollama API
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
import httpx
from dataclasses import dataclass


@dataclass
class OllamaModel:
    name: str
    size: str
    digest: str
    modified_at: str


class OllamaClient:
    """Klient do komunikacji z serwerem Ollama"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.timeout = httpx.Timeout(300.0)  # 5 minut timeout

    async def generate(self,
                       model: str,
                       prompt: str,
                       format: Optional[str] = None,
                       stream: bool = False,
                       **kwargs) -> str:
        """Generuje odpowiedź z modelu"""

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            **kwargs
        }

        if format:
            payload["format"] = format

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()

                if stream:
                    return await self._handle_stream_response(response)
                else:
                    result = response.json()
                    return result.get("response", "")

            except httpx.HTTPError as e:
                raise Exception(f"Błąd komunikacji z Ollama: {e}")
            except json.JSONDecodeError as e:
                raise Exception(f"Błąd parsowania odpowiedzi Ollama: {e}")

    async def generate_stream(self,
                              model: str,
                              prompt: str,
                              **kwargs) -> AsyncGenerator[str, None]:
        """Generuje strumieniową odpowiedź"""

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            **kwargs
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                        "POST",
                        f"{self.base_url}/api/generate",
                        json=payload
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue

            except httpx.HTTPError as e:
                raise Exception(f"Błąd komunikacji strumieniowej z Ollama: {e}")

    async def chat(self,
                   model: str,
                   messages: List[Dict[str, str]],
                   **kwargs) -> str:
        """Chat z modelem używając formatu wiadomości"""

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                return result.get("message", {}).get("content", "")

            except httpx.HTTPError as e:
                raise Exception(f"Błąd chat z Ollama: {e}")

    async def list_models(self) -> List[OllamaModel]:
        """Lista dostępnych modeli"""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()

                data = response.json()
                models = []

                for model_data in data.get("models", []):
                    model = OllamaModel(
                        name=model_data["name"],
                        size=model_data.get("size", ""),
                        digest=model_data.get("digest", ""),
                        modified_at=model_data.get("modified_at", "")
                    )
                    models.append(model)

                return models

            except httpx.HTTPError as e:
                raise Exception(f"Błąd pobierania listy modeli: {e}")

    async def pull_model(self, model_name: str) -> bool:
        """Pobiera model z repozytorium"""

        payload = {"name": model_name}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json=payload
                )
                response.raise_for_status()
                return True

            except httpx.HTTPError as e:
                print(f"Błąd pobierania modelu {model_name}: {e}")
                return False

    async def check_model_exists(self, model_name: str) -> bool:
        """Sprawdza czy model istnieje lokalnie"""

        models = await self.list_models()
        return any(model.name == model_name for model in models)

    async def ensure_model(self, model_name: str) -> bool:
        """Upewnia się, że model jest dostępny (pobiera jeśli nie ma)"""

        if await self.check_model_exists(model_name):
            return True

        print(f"Model {model_name} nie znaleziony. Pobieranie...")
        return await self.pull_model(model_name)

    async def health_check(self) -> bool:
        """Sprawdza czy serwer Ollama działa"""

        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
            except:
                return False

    async def _handle_stream_response(self, response) -> str:
        """Obsługuje strumieniową odpowiedź"""

        full_response = ""

        async for line in response.aiter_lines():
            if line.strip():
                try:
                    data = json.loads(line)
                    if "response" in data:
                        full_response += data["response"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue

        return full_response

    async def analyze_api_requirements(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Specjalna metoda do analizy wymagań API"""

        # Upewnij się, że model jest dostępny
        model = "llama3.1:8b"
        if not await self.ensure_model(model):
            # Fallback na mniejszy model
            model = "llama3.1:7b"
            if not await self.ensure_model(model):
                raise Exception("Nie można załadować żadnego modelu Llama")

        # Specjalistyczny prompt do analizy API
        prompt = self._create_api_analysis_prompt(text, language)

        try:
            response = await self.generate(
                model=model,
                prompt=prompt,
                format="json",
                temperature=0.3,  # Mniej kreatywności, więcej precyzji
                top_p=0.9
            )

            return json.loads(response)

        except json.JSONDecodeError as e:
            print(f"Błąd parsowania JSON z Ollama: {e}")
            print(f"Surowa odpowiedź: {response}")

            # Próba naprawy JSON
            cleaned_response = self._clean_json_response(response)
            try:
                return json.loads(cleaned_response)
            except:
                return self._create_fallback_analysis(text)

    def _create_api_analysis_prompt(self, text: str, language: str) -> str:
        """Tworzy specjalistyczny prompt do analizy API"""

        language_prompts = {
            "pl": """
Jesteś ekspertem w projektowaniu API. Przeanalizuj poniższy opis w języku polskim i wygeneruj specyfikację API.

Tekst do analizy: {text}

Zwróć dokładnie w tym formacie JSON (bez dodatkowych komentarzy):
{{
    "api_type": "rest",
    "name": "nazwa_api_bez_spacji",
    "description": "Krótki opis funkcjonalności API",
    "framework": "fastapi",
    "main_entities": ["encja1", "encja2"],
    "endpoints": [
        {{
            "path": "/sciezka",
            "method": "GET",
            "name": "nazwa_funkcji",
            "description": "Opis endpointu",
            "parameters": [
                {{
                    "name": "parametr",
                    "type": "string",
                    "required": true,
                    "description": "Opis parametru"
                }}
            ],
            "request_body": [],
            "response_body": [
                {{
                    "name": "pole_odpowiedzi",
                    "type": "string",
                    "description": "Opis pola"
                }}
            ]
        }}
    ],
    "auth_required": false,
    "database_required": true,
    "external_apis": []
}}
""",
            "en": """
You are an API design expert. Analyze the following English description and generate an API specification.

Text to analyze: {text}

Return exactly in this JSON format (no additional comments):
{{
    "api_type": "rest",
    "name": "api_name_no_spaces",
    "description": "Brief description of API functionality",
    "framework": "fastapi",
    "main_entities": ["entity1", "entity2"],
    "endpoints": [
        {{
            "path": "/path",
            "method": "GET",
            "name": "function_name",
            "description": "Endpoint description",
            "parameters": [
                {{
                    "name": "parameter",
                    "type": "string",
                    "required": true,
                    "description": "Parameter description"
                }}
            ],
            "request_body": [],
            "response_body": [
                {{
                    "name": "response_field",
                    "type": "string",
                    "description": "Field description"
                }}
            ]
        }}
    ],
    "auth_required": false,
    "database_required": true,
    "external_apis": []
}}
"""
        }

        template = language_prompts.get(language, language_prompts["en"])
        return template.format(text=text)

    def _clean_json_response(self, response: str) -> str:
        """Próbuje wyczyścić odpowiedź JSON"""

        # Usuń markdown code blocks
        response = response.replace("```json", "").replace("```", "")

        # Usuń dodatkowy tekst przed i po JSON
        start = response.find("{")
        end = response.rfind("}") + 1

        if start != -1 and end != 0:
            return response[start:end]

        return response

    def _create_fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Tworzy fallback analizę gdy LLM zawiedzie"""

        return {
            "api_type": "rest",
            "name": "generated_api",
            "description": "API generated from text description",
            "framework": "fastapi",
            "main_entities": ["item"],
            "endpoints": [
                {
                    "path": "/items",
                    "method": "GET",
                    "name": "list_items",
                    "description": "Get list of items",
                    "parameters": [],
                    "request_body": [],
                    "response_body": [
                        {
                            "name": "items",
                            "type": "array",
                            "description": "List of items"
                        }
                    ]
                }
            ],
            "auth_required": False,
            "database_required": True,
            "external_apis": []
        }