# text2api 🚀

**Automatyczne generowanie API z opisu tekstowego używając NLP i Ollama**

text2api to zaawansowane narzędzie, które automatycznie generuje kompletne API na podstawie opisu w języku naturalnym. Wykorzystuje modele językowe (Ollama) do analizy tekstu i generuje kod, dokumentację, testy i pliki Docker.

## ✨ Cechy

- 🤖 **NLP Analysis** - Inteligentna analiza tekstu używając Ollama
- 🌍 **Wielojęzyczność** - Obsługa polskiego, angielskiego i innych języków
- 🔧 **Wiele protokołów** - REST, GraphQL, gRPC, WebSocket, CLI
- 📦 **Kompletne projekty** - Kod + Docker + testy + dokumentacja
- ⚡ **Framework'i** - FastAPI, Flask, Graphene, Click i inne
- 🔐 **Autoryzacja** - JWT, OAuth, basic auth
- 💾 **Bazy danych** - PostgreSQL, SQLite, MongoDB
- 🐳 **Docker ready** - Gotowe do deploymentu

## 🚀 Szybki start

### Instalacja z Poetry

```bash
# Klonuj repozytorium
git clone https://github.com/username/text2api.git
cd text2api

# Zainstaluj z Poetry
poetry install

# Aktywuj środowisko
poetry shell
```

### Instalacja z pip

```bash
pip install text2api
```

### Docker (zalecane)

```bash
# Uruchom kompletne środowisko
docker-compose up -d

# Użyj text2api
docker-compose exec text2api text2api generate "API do zarządzania użytkownikami"
```

## 📋 Wymagania

- **Python 3.9+**
- **Ollama** - dla analizy NLP
- **Docker** (opcjonalnie) - dla konteneryzacji

### Instalacja Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Uruchom serwer
ollama serve

# Pobierz zalecany model
ollama pull llama3.1:8b
```

## 💡 Przykłady użycia

### Podstawowe użycie

```bash
# Generuj REST API
text2api generate "API do zarządzania produktami sklepu z kategoriami i cenami"

# Wymusi określony typ
text2api generate "System czatu" --type websocket

# Określ framework
text2api generate "Blog API" --framework flask

# Bez Dockera
text2api generate "Todo API" --no-docker
```

### Tryb interaktywny

```bash
text2api generate-from-file --interactive
```

### Sprawdź status

```bash
# Sprawdź Ollama i modele
text2api check

# Lista projektów
text2api list-projects

# Info o projekcie
text2api info ./generated_apis/my_api
```

### Z pliku

```bash
# Utwórz plik opisu
echo "API dla systemu rezerwacji hoteli z pokojami i gośćmi" > api_description.txt

# Generuj z pliku
text2api generate-from-file --file api_description.txt
```

## 🎯 Obsługiwane typy API

### 🌐 REST API
- **FastAPI** - Nowoczesne, szybkie API z automatyczną dokumentacją
- **Flask** - Klasyczny, prosty framework
- Automatyczna walidacja Pydantic
- OpenAPI/Swagger dokumentacja
- Middleware CORS
- Autoryzacja JWT

### 📊 GraphQL
- **Graphene** - Pełna implementacja GraphQL
- Schema auto-generation
- Resolvers dla CRUD operacji
- Subscription support dla real-time

### ⚡ gRPC
- **Protocol Buffers** - Definicje schema
- Wysokowydajne RPC
- Streaming support
- Multi-platform compatibility

### 🔌 WebSocket
- **Real-time komunikacja**
- Event-driven architecture
- Room management
- Broadcasting

### 🖥️ CLI Tools
- **Click framework**
- Argumenty i opcje
- Kolorowe output (Rich)
- Pluggable commands

## 📁 Struktura wygenerowanego projektu

```
my_api/
├── main.py              # Główny plik aplikacji
├── models.py            # Modele danych
├── requirements.txt     # Zależności Python
├── Dockerfile          # Konteneryzacja
├── docker-compose.yml  # Kompletne środowisko
├── .env.example        # Zmienne środowiskowe
├── api_spec.json       # Specyfikacja API
├── README.md           # Dokumentacja projektu
├── tests/              # Testy automatyczne
│   ├── test_api.py
│   └── conftest.py
└── docs/               # Dokumentacja
    ├── api.md
    └── deployment.md
```

## 🎨 Przykłady opisów

### Proste API
```
"API do zarządzania książkami z autorami i kategoriami"
"System logowania użytkowników z rejestracją"
"Todo list z projektami i terminami"
```

### Złożone systemy
```
"E-commerce platform z produktami, koszykiem, płatnościami, 
użytkownikami, zamówieniami, recenzjami i systemem promocji"

"System zarządzania projektami z zadaniami, zespołami, 
timetrackingiem, raportami i integracjami Git"
```

### Różne protokoły
```
"GraphQL API dla mediów społecznościowych"  # -> GraphQL
"Mikrousługa płatności"                     # -> gRPC  
"Serwer czatu w czasie rzeczywistym"        # -> WebSocket
"CLI do konwersji plików"                   # -> Click
```

## 🔧 Konfiguracja

### Zmienne środowiskowe

```bash
# .env
OLLAMA_URL=http://localhost:11434
GENERATED_APIS_DIR=./generated_apis
DEFAULT_FRAMEWORK=fastapi
DEFAULT_DATABASE=postgresql
SECRET_KEY=your-secret-key
```

### Konfiguracja Ollama

```bash
# Sprawdź dostępne modele
text2api models

# Pobierz zalecane modele
ollama pull llama3.1:8b
ollama pull llama3.1:7b
ollama pull codellama:7b
```

## 🐳 Docker

### Rozwój lokalny

```bash
# Zbuduj obraz
docker build -t text2api .

# Uruchom z volumami
docker run -v $(pwd)/generated_apis:/app/generated_apis \
           -v /var/run/docker.sock:/var/run/docker.sock \
           text2api generate "My API description"
```

### Docker Compose

```bash
# Pełne środowisko
docker-compose up -d

# Tylko podstawowe usługi
docker-compose up -d ollama text2api postgres

# Sprawdź logi
docker-compose logs -f text2api
```

### Usługi w Docker Compose

- **ollama** - Serwer LLM na porcie 11434
- **text2api** - Główne narzędzie
- **postgres** - Baza danych na porcie 5432
- **redis** - Cache na porcie 6379
- **nginx** - Reverse proxy na porcie 80
- **adminer** - Web UI bazy danych na porcie 8080
- **portainer** - Docker management na porcie 9000
- **jupyter** - Notebooks na porcie 8888

## 🧪 Testy

```bash
# Uruchom testy
poetry run pytest

# Z coverage
poetry run pytest --cov=text2api

# Testy konkretnego modułu
poetry run pytest tests/test_analyzer.py
```

## 📚 Dokumentacja API

Każde wygenerowane API zawiera:

- **OpenAPI/Swagger** - Interaktywna dokumentacja
- **README.md** - Instrukcje instalacji i użycia
- **docs/api.md** - Szczegółowa dokumentacja endpointów
- **docs/deployment.md** - Instrukcje wdrożenia

### Dostęp do dokumentacji

```bash
# FastAPI
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc

# Flask
http://localhost:5000/swagger   # Flask-RESTX
```

## 🔌 Integracje

### Model Context Protocol (MCP)

text2api obsługuje MCP do zaawansowanej integracji z LLM:

```python
from text2api.core.mcp_integration import MCPIntegration

mcp = MCPIntegration()
enhanced_spec = await mcp.enhance_spec(api_spec)
```

### Zewnętrzne API

Automatyczne rozpoznawanie i generowanie klientów dla:
- REST APIs
- GraphQL endpoints  
- Third-party services
- Database connections

## 🎯 Roadmap

### v0.2.0
- [ ] Więcej frameworków (Django, Spring Boot)
- [ ] TypeScript/Node.js support
- [ ] Automatic OpenAPI import
- [ ] Cloud deployment templates

### v0.3.0
- [ ] Visual API designer
- [ ] Real-time collaboration
- [ ] CI/CD integration
- [ ] Performance optimization

### v1.0.0
- [ ] Production-ready
- [ ] Enterprise features
- [ ] SaaS platform
- [ ] Plugin ecosystem

## 🤝 Wkład w projekt

Zapraszamy do współpracy! 

```bash
# Fork repozytorium
git clone https://github.com/yourusername/text2api.git

# Utwórz branch dla feature
git checkout -b feature/amazing-feature

# Zacommituj zmiany
git commit -m "Add amazing feature"

# Push do brancha
git push origin feature/amazing-feature

# Utwórz Pull Request
```

### Standardy kodu

- **Black** - formatowanie kodu
- **isort** - sortowanie importów  
- **flake8** - linting
- **mypy** - type checking
- **pytest** - testy

```bash
# Uruchom wszystkie sprawdzenia
poetry run black text2api/
poetry run isort text2api/
poetry run flake8 text2api/
poetry run mypy text2api/
poetry run pytest
```

## 🐛 Zgłaszanie błędów

Znalazłeś błąd? [Utwórz issue](https://github.com/username/text2api/issues)

Podaj:
- Opis problemu
- Kroki do reprodukcji
- Oczekiwane zachowanie
- Wersję text2api i Python
- Logi błędów

## 📄 Licencja

MIT License - zobacz [LICENSE](LICENSE) dla szczegółów.

## 👥 Autorzy

- **Your Name** - Główny developer
- **Contributors** - Zobacz [CONTRIBUTORS.md](CONTRIBUTORS.md)

## 🙏 Podziękowania

- **Ollama** - Za wspaniały lokalny LLM server
- **FastAPI** - Za nowoczesny framework API
- **Anthropic** - Za inspirację i wsparcie AI
- **Community** - Za feedback i contribucje

## 📞 Wsparcie

- 📧 Email: support@text2api.dev
- 💬 Discord: [text2api Community](https://discord.gg/text2api)
- 📖 Docs: [docs.text2api.dev](https://docs.text2api.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/username/text2api/issues)

---

**Made with ❤️ and 🤖 AI**

*text2api - Transform ideas into APIs instantly*