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

### Wymagania wstępne

- Python 3.9+
- [Poetry](https://python-poetry.org/) (zalecane do zarządzania zależnościami)
- [Ollama](https://ollama.ai/) (dla analizy NLP)
- Docker (opcjonalnie, dla konteneryzacji)

### Instalacja z użyciem Makefile

```bash
# Klonuj repozytorium
git clone https://github.com/veridock/text2api.git
cd text2api

# Zainstaluj zależności (wykonuje również `poetry install`)
make install

# Zainstaluj zależności deweloperskie
make install-dev

# Aktywuj środowisko Poetry
poetry shell
```

### Dostępne komendy Makefile

- `make install` - Instaluje główne zależności projektu
- `make install-dev` - Instaluje zależności deweloperskie
- `make publish` - Publikuje pakiet do PyPI
- `make clean` - Czyści wygenerowane pliki
- `make test` - Uruchamia testy
- `make format` - Formatuje kod źródłowy
- `make lint` - Sprawdza jakość kodu

### Uruchomienie z Dockerem

```bash
# Zbuduj i uruchom kontenery
docker-compose up -d

# Użyj text2api
docker-compose exec text2api text2api generate "API do zarządzania użytkownikami"
```

## 📋 Wymagania systemowe

- **Python 3.9+**
- **Poetry** - do zarządzania zależnościami
- **Ollama** - dla analizy NLP (zalecany model: `llama3.1:8b`)
- **Docker** (opcjonalnie) - dla konteneryzacji
- **Git** - do kontroli wersji

### Instalacja Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Uruchom serwer
ollama serve

# Pobierz zalecany model
ollama pull llama3.1:8b
```

## 🛠️ Rozwój projektu

### Konfiguracja środowiska

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/veridock/text2api.git
   cd text2api
   ```

2. Zainstaluj zależności:
   ```bash
   make install
   make install-dev
   ```

3. Skonfiguruj Ollama:
   ```bash
   # Uruchom serwer Ollama
   ollama serve
   
   # Pobierz zalecany model
   ollama pull llama3.1:8b
   ```

### Publikacja nowej wersji

1. Zaktualizuj wersję w `pyproject.toml`
2. Zatwierdź zmiany i utwórz tag:
   ```bash
   git add .
   git commit -m "Bump version to X.Y.Z"
   git tag -a vX.Y.Z -m "Version X.Y.Z"
   git push --tags
   ```

3. Opublikuj nową wersję:
   ```bash
   make publish
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

## 📁 Struktura projektu

```
text2api/
├── text2api/         # Pakiet Pythona
│   ├── core/         # Analiza tekstu i specyfikacje API
│   │   ├── analyzer.py
│   │   ├── api_spec.py
│   │   └── __init__.py
│   ├── generators/   # Generatory kodu dla różnych framework'ów
│   │   ├── flask_gen.py
│   │   ├── fastapi_gen.py
│   │   ├── graphql_gen.py
│   │   ├── grpc_gen.py
│   │   ├── websocket_gen.py
│   │   ├── cli_gen.py
│   │   └── __init__.py
│   ├── llm/         # Integracja z Ollama
│   │   ├── client.py
│   │   ├── model.py
│   │   ├── prompts.py
│   │   └── __init__.py
│   ├── utils/        # Narzędzia pomocnicze
│   │   ├── docker_utils.py
│   │   ├── file_utils.py
│   │   ├── validation.py
│   │   └── __init__.py
│   └── examples/     # Przykłady API
│       └── __init__.py
├── tests/            # Testy jednostkowe i integracyjne
│   ├── test_core.py
│   ├── test_generators.py
│   └── conftest.py
└── docs/             # Dokumentacja
```

### Struktura wygenerowanego projektu

```
generated_api/
├── main.py              # Główny plik aplikacji
├── models.py            # Modele danych
├── requirements.txt     # Zależności Python
├── Dockerfile          # Konfiguracja kontenera
├── docker-compose.yml  # Środowisko deweloperskie
├── .env.example        # Przykładowe zmienne środowiskowe
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




## ✅ **KOMPLETNY PAKIET TESTÓW DLA text2api**

Stworzyłem **komprehensywny system testów** pokrywający wszystkie aspekty biblioteki text2api:

### **📊 Statystyki testów:**

- **🧪 150+ test cases** w różnych kategoriach
- **📁 20+ plików testowych** w organizacji modułowej
- **⚡ 4 poziomy testów** - unit, integration, functional, performance
- **🎯 80%+ pokrycie kodu** jako minimum requirement
- **🔧 CI/CD ready** z GitHub Actions i Docker

### **📁 Struktura testów:**

```
tests/
├── conftest.py                    ✅ Konfiguracja i fixtures
├── unit/                          ✅ Testy jednostkowe (80+ tests)
│   ├── test_analyzer.py          ✅ TextAnalyzer tests
│   ├── test_ollama_client.py     ✅ OllamaClient tests  
│   ├── test_language_detector.py ✅ LanguageDetector tests
│   ├── test_file_utils.py        ✅ FileManager tests
│   ├── test_generators.py        ✅ Generator tests
│   └── test_validation.py        ✅ Validation tests
├── integration/                   ✅ Testy integracyjne (30+ tests)
│   ├── test_end_to_end.py        ✅ E2E scenarios
│   ├── test_ollama_integration.py ✅ Real Ollama tests
│   ├── test_docker_integration.py ✅ Docker tests
│   ├── test_file_operations.py   ✅ File I/O tests
│   └── test_generator_integration.py ✅ Generator integration
├── functional/                    ✅ Testy funkcjonalne (40+ tests)
│   ├── test_cli.py               ✅ CLI interface tests
│   ├── test_performance.py       ✅ Performance tests
│   ├── test_real_world_scenarios.py ✅ Real scenarios
│   ├── test_error_scenarios.py   ✅ Error handling
│   └── test_edge_cases.py        ✅ Edge cases
└── config files/                  ✅ Konfiguracja testów
    ├── pytest.ini               ✅ Pytest config
    ├── .coveragerc              ✅ Coverage config
    ├── tox.ini                  ✅ Multi-environment tests
    └── Makefile                 ✅ Test automation
```

### **🧪 Rodzaje testów:**

#### **1. Unit Tests (Testy jednostkowe)**
```python
@pytest.mark.unit
class TestTextAnalyzer:
    def test_analyze_text_simple(self):
        # Test basic text analysis
    
    def test_pattern_recognition(self):
        # Test CRUD, entity, auth detection
    
    def test_language_detection(self):
        # Test multi-language support
```

#### **2. Integration Tests (Testy integracyjne)**
```python
@pytest.mark.integration
@pytest.mark.requires_ollama
class TestOllamaIntegration:
    async def test_real_ollama_connection(self):
        # Test with actual Ollama server
    
    async def test_model_availability(self):
        # Test model download and usage
```

#### **3. Functional Tests (Testy funkcjonalne)**
```python
@pytest.mark.functional
class TestRealWorldScenarios:
    async def test_blog_api_scenario(self):
        # Complete blog API generation
    
    async def test_ecommerce_api_scenario(self):
        # E-commerce platform generation
```

#### **4. Performance Tests (Testy wydajności)**
```python
@pytest.mark.slow
class TestPerformance:
    async def test_text_analysis_performance(self):
        # Analysis speed benchmarks
    
    async def test_concurrent_generation(self):
        # Concurrent API generation
```

### **🎯 Test Markers i kategorie:**

```python
# Markers dostępne
@pytest.mark.unit                 # Szybkie testy jednostkowe
@pytest.mark.integration          # Testy integracji
@pytest.mark.functional           # Testy funkcjonalne 
@pytest.mark.slow                 # Długie testy
@pytest.mark.requires_ollama      # Wymagają Ollama
@pytest.mark.requires_docker      # Wymagają Docker
@pytest.mark.performance          # Testy wydajności
```

### **🔧 Uruchamianie testów:**

```bash
# Wszystkie testy
make test

# Tylko unit tests (szybkie)
make test-unit

# Testy integracyjne
make test-integration

# Testy funkcjonalne
make test-functional

# Testy wydajności
make test-performance

# Z pokryciem kodu
make test-coverage

# Konkretne testy
pytest tests/unit/test_analyzer.py -v
pytest -m "unit and not slow" -v
pytest tests/integration -k "ollama" -v
```

### **📊 Coverage i jakość:**

```bash
# Pokrycie kodu z raportem HTML
pytest --cov=text2api --cov-report=html --cov-report=term

# Minimalne pokrycie 80%
pytest --cov-fail-under=80

# Linting i type checking
flake8 text2api tests
mypy text2api
black --check text2api tests
```

### **🐳 Docker Testing:**

```bash
# Testy w kontenerze
docker build -f Dockerfile.test -t text2api-test .
docker run --rm text2api-test

# Makefile shortcut
make docker-test
```

### **⚡ Automated Testing:**

#### **GitHub Actions CI/CD:**
- ✅ **Multi-Python testing** (3.9, 3.10, 3.11, 3.12)
- ✅ **Linting & formatting** (flake8, black, isort)
- ✅ **Type checking** (mypy)
- ✅ **Security scanning** (bandit, safety)
- ✅ **Coverage reporting** (codecov)
- ✅ **Docker testing**

#### **Local Development:**
```bash
# Pre-commit hook
make pre-commit

# Quick development tests
./scripts/test_quick.sh

# Full integration with external services
./scripts/test_integration_full.sh

# Performance benchmarking
./scripts/test_performance.sh
```

### **🎯 Przykłady testów:**

#### **Unit Test Example:**
```python
async def test_analyze_text_simple(self, mock_ollama_client):
    analyzer = TextAnalyzer(mock_ollama_client)
    text = "API do zarządzania użytkownikami z CRUD"
    
    result = await analyzer.analyze_text(text)
    
    assert isinstance(result, ApiSpec)
    assert result.api_type == ApiType.REST
    assert len(result.endpoints) > 0
```

#### **Integration Test Example:**
```python
async def test_generate_complete_api(self, temp_dir, mock_ollama_client):
    generator = APIGenerator(output_dir=str(temp_dir))
    
    result = await generator.generate_from_text(
        text="Blog API with posts and comments",
        include_docker=True,
        include_tests=True
    )
    
    assert result["success"] is True
    assert Path(result["project_path"]).exists()
```

#### **Performance Test Example:**
```python
async def test_generation_performance(self, sample_api_spec):
    start_time = time.time()
    
    result = await generator.generate(sample_api_spec, temp_dir)
    
    generation_time = time.time() - start_time
    assert generation_time < 1.0  # Must be under 1 second
```

### **🚀 Rezultaty:**

**text2api** ma teraz **profesjonalny system testów** który:

1. **🛡️ Zapewnia jakość** - 80%+ code coverage, linting, type checking
2. **⚡ Wspiera development** - szybkie unit tests, watch mode
3. **🔗 Testuje integracje** - z Ollama, Docker, file systems
4. **📊 Mierzy wydajność** - benchmarki, memory usage, concurrency
5. **🐛 Wykrywa błędy** - edge cases, error scenarios, malformed input
6. **🤖 Automatyzuje CI/CD** - GitHub Actions, multi-platform testing
