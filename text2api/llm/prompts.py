
"""
Prompts and templates for LLM interactions
"""

# Systemowe prompty dla różnych języków
SYSTEM_PROMPTS = {
    'pl': """Jesteś ekspertem w projektowaniu API. Analizujesz opisy w języku polskim i generujesz specyfikacje API.

Zwróć specyfikację w formacie JSON zawierającą:
- typ API (rest/graphql/grpc/websocket/cli)
- główne encje/modele
- endpointy z parametrami
- wymagania dotyczące bazy danych i autoryzacji

Odpowiedz TYLKO kodem JSON, bez dodatkowych komentarzy.""",

    'en': """You are an API design expert. You analyze English descriptions and generate API specifications.

Return a JSON specification containing:
- API type (rest/graphql/grpc/websocket/cli)
- main entities/models
- endpoints with parameters
- database and authentication requirements

Respond with ONLY JSON code, no additional comments."""
}

# Prompty dla różnych typów API
API_TYPE_PROMPTS = {
    'rest': """
Generuj REST API z endpointami HTTP używającymi GET, POST, PUT, DELETE.
Uwzględnij paginację, filtrowanie i walidację.
""",

    'graphql': """
Generuj GraphQL schema z queries, mutations i subscription.
Uwzględnij relacje między typami i optymalizację zapytań.
""",

    'grpc': """
Generuj gRPC service z protokołem buffers.
Uwzględnij streaming i obsługę błędów.
""",

    'websocket': """
Generuj WebSocket API z real-time komunikacją.
Uwzględnij rooms, broadcasting i zarządzanie połączeniami.
""",

    'cli': """
Generuj CLI tool z komendami, argumentami i opcjami.
Uwzględnij import/export danych i interaktywność.
"""
}

# Prompty dla różnych domen
DOMAIN_PROMPTS = {
    'ecommerce': """
Dla e-commerce zawrzyj:
- Produkty z kategoriami i wariantami
- Koszyk i zarządzanie zamówieniami
- System płatności i faktury
- Recenzje i oceny
- Zarządzanie inventory
""",

    'blog': """
Dla bloga zawrzyj:
- Posty z tagami i kategoriami
- System komentarzy
- Zarządzanie użytkownikami i autorami
- SEO metadata
- Moderacja treści
""",

    'cms': """
Dla CMS zawrzyj:
- Zarządzanie treścią i mediami
- System uprawnień i ról
- Wersjonowanie treści
- Workflow publikacji
- Multi-language support
"""
}

def create_analysis_prompt(text: str, language: str = 'en', api_type: str = None, domain: str = None) -> str:
    """
    Tworzy prompt do analizy tekstu
    
    Args:
        text: Tekst do analizy
        language: Język ('pl', 'en', etc.)
        api_type: Typ API (opcjonalny)
        domain: Domena aplikacji (opcjonalny)
    
    Returns:
        Kompletny prompt
    """
    
    # Bazowy prompt systemowy
    system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS['en'])
    
    # Dodaj specyficzne instrukcje dla typu API
    if api_type and api_type in API_TYPE_PROMPTS:
        system_prompt += "\n\n" + API_TYPE_PROMPTS[api_type]
    
    # Dodaj instrukcje dla domeny
    if domain and domain in DOMAIN_PROMPTS:
        system_prompt += "\n\n" + DOMAIN_PROMPTS[domain]
    
    # Kompletny prompt
    full_prompt = f"""{system_prompt}

Tekst do analizy: {text}

Zwróć specyfikację API w tym formacie JSON:
{{
    "api_type": "rest|graphql|grpc|websocket|cli",
    "name": "nazwa_api_bez_spacji",
    "description": "Opis funkcjonalności API",
    "framework": "fastapi|flask|graphene|grpc|websockets|click",
    "main_entities": ["encja1", "encja2"],
    "endpoints": [
        {{
            "path": "/sciezka",
            "method": "GET|POST|PUT|DELETE",
            "name": "nazwa_funkcji",
            "description": "Opis endpointu",
            "parameters": [
                {{
                    "name": "parametr",
                    "type": "string|integer|boolean|float",
                    "required": true,
                    "description": "Opis parametru"
                }}
            ],
            "request_body": [],
            "response_body": []
        }}
    ],
    "auth_required": false,
    "database_required": true,
    "external_apis": []
}}
"""
    
    return full_prompt
