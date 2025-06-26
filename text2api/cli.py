"""
CLI interface dla text2api
"""

import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from pathlib import Path
import json

from .core.generator import APIGenerator
from .llm.ollama_client import OllamaClient
from .examples.sample_descriptions import SAMPLE_DESCRIPTIONS

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    text2api - Automatyczne generowanie API z opisu tekstowego

    Narzędzie używa NLP (Ollama) do analizy tekstu i generowania kompletnego API
    z kodem, dokumentacją i plikami Docker.
    """
    pass


@cli.command()
@click.argument('description', type=str)
@click.option('--output', '-o', default=None, help='Nazwa folderu wyjściowego')
@click.option('--type', '-t', type=click.Choice(['rest', 'graphql', 'grpc', 'websocket', 'cli']),
              help='Wymusza określony typ API')
@click.option('--framework', '-f', help='Wymusza określony framework')
@click.option('--no-docker', is_flag=True, help='Nie generuj plików Docker')
@click.option('--no-tests', is_flag=True, help='Nie generuj testów')
@click.option('--no-docs', is_flag=True, help='Nie generuj dokumentacji')
@click.option('--ollama-url', default='http://localhost:11434', help='URL serwera Ollama')
@click.option('--output-dir', default='./generated_apis', help='Katalog bazowy dla projektów')
def generate(description, output, type, framework, no_docker, no_tests, no_docs, ollama_url, output_dir):
    """
    Generuje API na podstawie opisu tekstowego

    DESCRIPTION: Opis funkcjonalności API w języku naturalnym

    Przykłady:
    text2api generate "API do zarządzania użytkownikami z CRUD operations"
    text2api generate "GraphQL API dla sklepu internetowego" --type graphql
    text2api generate "CLI tool do konwersji plików" --type cli
    """

    async def _generate():
        generator = APIGenerator(output_dir=output_dir, ollama_url=ollama_url)

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
        ) as progress:
            task = progress.add_task("🔍 Analizuję opis...", total=None)

            try:
                # Use the correct generate method with the API type if specified
                api_type = type if type else "rest"
                result = await generator.generate(
                    description=description,
                    api_type=api_type,
                    framework=framework if framework else "fastapi"
                )

                progress.remove_task(task)


                if result.get('status') == 'success':
                    project_path = result.get('project_dir', 'unknown')
                    console.print(Panel.fit(
                        f"✅ API wygenerowane pomyślnie!\n\n"
                        f"📁 Lokalizacja: {project_path}\n"
                        f"🔧 Typ API: {result.get('api_type', 'unknown')}\n"
                        f"⚡ Framework: {result.get('framework', 'unknown')}\n"
                        f"📄 Pliki: {', '.join(result.get('files_generated', []))}",
                        title="Sukces",
                        border_style="green"
                    ))

                    # Pokaż instrukcje
                    if result['instructions']:
                        console.print("\n📋 Instrukcje uruchomienia:")
                        for i, instruction in enumerate(result['instructions'], 1):
                            console.print(f"  {i}. {instruction}")

                else:
                    console.print(Panel.fit(
                        f"❌ Błąd generowania:\n{result['error']}",
                        title="Błąd",
                        border_style="red"
                    ))

            except Exception as e:
                console.print(Panel.fit(
                    f"❌ Błąd wykonania:\n{str(e)}",
                    title="Błąd",
                    border_style="red"
                ))

        # Sprawdź status Ollama
        try:
            client = OllamaClient(base_url=ollama_url)
            models = await client.list_models()
            
            if models:
                console.print("\n✅ Ollama działa poprawnie!")
                console.print(f"   Modele: {', '.join(models)}")
            else:
                console.print("\n⚠️ Ollama działa, ale nie ma modeli!")
                console.print("   Uruchom: ollama pull llama3.1:8b")
        except Exception as e:
            console.print("\n❌ Ollama nie działa!")
            console.print(f"   Błąd: {str(e)}")
            console.print("   Sprawdź czy serwer działa na {ollama_url}")
            console.print("   Uruchom: ollama serve")

    asyncio.run(_generate())


@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def info(project_path):
    """
    Pokazuje informacje o wygenerowanym projekcie
    """

    project_path = Path(project_path)
    spec_file = project_path / "api_spec.json"

    if not spec_file.exists():
        console.print(f"❌ Brak pliku api_spec.json w {project_path}")
        return

    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec = json.load(f)

        # Podstawowe info
        console.print(Panel.fit(
            f"📋 {spec['name']}\n"
            f"📝 {spec['description']}\n"
            f"🔧 {spec['api_type'].upper()} API ({spec['framework']})\n"
            f"🌍 Język: {spec['language']}\n"
            f"🔐 Auth: {'✅' if spec.get('auth_type') else '❌'}\n"
            f"💾 Database: {'✅' if spec.get('database_required') else '❌'}",
            title="Informacje o projekcie",
            border_style="blue"
        ))

        # Endpointy
        if spec.get('endpoints'):
            console.print("\n🛣️  Endpointy:")

            endpoint_table = Table()
            endpoint_table.add_column("Method", style="cyan")
            endpoint_table.add_column("Path", style="magenta")
            endpoint_table.add_column("Nazwa", style="green")
            endpoint_table.add_column("Opis", style="yellow")

            for endpoint in spec['endpoints']:
                endpoint_table.add_row(
                    endpoint['method'],
                    endpoint['path'],
                    endpoint['name'],
                    endpoint.get('description', '')[:50] + ('...' if len(endpoint.get('description', '')) > 50 else '')
                )

            console.print(endpoint_table)

        # Modele
        if spec.get('models'):
            console.print(f"\n📊 Modele danych: {len(spec['models'])}")
            for model in spec['models']:
                console.print(f"   • {model['name']} ({len(model.get('fields', []))} pól)")

        # Pliki w projekcie
        files = list(project_path.rglob('*'))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]

        console.print(f"\n📁 Pliki w projekcie: {len(files)}")

        # Sprawdź czy da się uruchomić
        if (project_path / "requirements.txt").exists():
            console.print("\n🚀 Aby uruchomić:")
            console.print(f"   cd {project_path}")
            console.print("   pip install -r requirements.txt")

            if spec['framework'] == 'fastapi':
                console.print("   uvicorn main:app --reload")
                console.print("   Dokumentacja: http://localhost:8000/docs")
            elif spec['framework'] == 'flask':
                console.print("   python app.py")
                console.print("   API: http://localhost:5000")
            elif spec['api_type'] == 'cli':
                console.print("   python cli.py --help")

            if (project_path / "docker-compose.yml").exists():
                console.print("\n🐳 Lub z Docker:")
                console.print("   docker-compose up -d")

    except Exception as e:
        console.print(f"❌ Błąd odczytu specyfikacji: {e}")


@cli.command()
@click.argument('input_spec', type=click.Path(exists=True))
@click.option('--output', '-o', help='Nazwa nowego projektu')
@click.option('--framework', '-f', help='Zmień framework')
def regenerate(input_spec, output, framework):
    """
    Regeneruje projekt na podstawie istniejącej specyfikacji

    INPUT_SPEC: Ścieżka do pliku api_spec.json
    """

    async def _regenerate():
        try:
            with open(input_spec, 'r', encoding='utf-8') as f:
                spec_data = json.load(f)

            # Zmień framework jeśli podano
            if framework:
                spec_data['framework'] = framework

            console.print(f"🔄 Regeneruję projekt: {spec_data['name']}")

            generator = APIGenerator()

            # Konwertuj z powrotem na ApiSpec object (potrzebne dodatkowe mapowanie)
            # Tutaj uproszczenie - w pełnej implementacji trzeba by zrekonstruować obiekt
            console.print("⚠️  Funkcja regenerate wymaga dodatkowej implementacji")
            console.print("💡 Na razie użyj 'text2api generate' z nowym opisem")

        except Exception as e:
            console.print(f"❌ Błąd regeneracji: {e}")

    asyncio.run(_regenerate())


@cli.command()
def list_projects():
    """
    Listuje wygenerowane projekty
    """

    projects_dir = Path("./generated_apis")

    if not projects_dir.exists():
        console.print("📂 Brak folderu z projektami (./generated_apis)")
        return

    projects = []
    for item in projects_dir.iterdir():
        if item.is_dir():
            spec_file = item / "api_spec.json"
            if spec_file.exists():
                try:
                    with open(spec_file, 'r', encoding='utf-8') as f:
                        spec = json.load(f)
                    projects.append((item.name, spec))
                except:
                    projects.append((item.name, None))

    if not projects:
        console.print("📭 Brak wygenerowanych projektów")
        return

    console.print(f"📋 Znalezione projekty ({len(projects)}):\n")

    table = Table()
    table.add_column("Nazwa", style="cyan")
    table.add_column("Typ", style="magenta")
    table.add_column("Framework", style="green")
    table.add_column("Opis", style="yellow")

    for name, spec in projects:
        if spec:
            table.add_row(
                name,
                spec.get('api_type', 'unknown').upper(),
                spec.get('framework', 'unknown'),
                spec.get('description', '')[:40] + ('...' if len(spec.get('description', '')) > 40 else '')
            )
        else:
            table.add_row(name, "❌", "❌", "Błędna specyfikacja")

    console.print(table)

    console.print(f"\n💡 Użyj 'text2api info ./generated_apis/NAZWA' dla szczegółów")


@cli.command()
@click.option('--url', default='http://localhost:11434', help='URL serwera Ollama')
def models(url):
    """
    Zarządzaj modelami Ollama
    """

    async def _models():
        ollama_client = OllamaClient(base_url=url)

        try:
            models = await ollama_client.list_models()

            if not models:
                console.print("📭 Brak zainstalowanych modeli")
                console.print("\n💡 Pobierz zalecany model:")
                console.print("   ollama pull llama3.1:8b")
                return

            table = Table(title=f"Modele Ollama ({url})")
            table.add_column("Nazwa", style="cyan")
            table.add_column("Rozmiar", style="magenta")
            table.add_column("Zmodyfikowany", style="green")

            for model in models:
                table.add_row(
                    model.name,
                    model.size,
                    model.modified_at[:19] if model.modified_at else "unknown"
                )

            console.print(table)

            # Sprawdź zalecane
            recommended = ['llama3.1:8b', 'llama3.1:7b', 'llama3:8b']
            available = [m.name for m in models]
            missing = [m for m in recommended if m not in available]

            if missing:
                console.print(f"\n⚠️  Zalecane modele do pobrania: {', '.join(missing)}")
                console.print("   ollama pull <model_name>")

        except Exception as e:
            console.print(f"[red]Błąd podczas sprawdzania modeli: {e}")
            console.print("[yellow]Upewnij się, że serwer Ollama jest uruchomiony i dostępny pod podanym adresem.")
            return

    asyncio.run(_models())


def main():
    """Main entry point for the CLI."""
    try:
        return cli()
    except KeyboardInterrupt:
        console.print("\n👋 Przerwano przez użytkownika")
        return 1
    except Exception as e:
        console.print(Panel.fit(
            f"💥 Nieoczekiwany błąd:\n{str(e)}",
            title="Krytyczny błąd",
            border_style="red"
        ))
        return 1
    return 0


if __name__ == "__main__":
    main()


@cli.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Plik z opisem')
@click.option('--interactive', '-i', is_flag=True, help='Tryb interaktywny')
def generate_from_file(file, interactive):
    """
    Generuje API z pliku tekstowego lub w trybie interaktywnym
    """

    if interactive:
        _interactive_mode()
    elif file:
        with open(file, 'r', encoding='utf-8') as f:
            description = f.read()

        console.print(f"📖 Wczytano opis z pliku: {file}")
        console.print(Panel(description[:200] + "...", title="Podgląd opisu"))

        if click.confirm("Kontynuować generowanie?"):
            # Użyj komendy generate
            from click.testing import CliRunner
            runner = CliRunner()
            runner.invoke(generate, [description])
    else:
        console.print("❌ Podaj --file lub użyj --interactive")


def _interactive_mode():
    """Tryb interaktywny"""

    console.print(Panel.fit(
        "🤖 Tryb interaktywny text2api\n\n"
        "Opisz swoją aplikację, a ja wygeneruję dla Ciebie kompletne API!",
        title="text2api Interactive",
        border_style="blue"
    ))

    # Zbierz informacje
    description = click.prompt("\n📝 Opisz funkcjonalność API", type=str)

    api_type = click.prompt(
        "🔧 Typ API",
        type=click.Choice(['rest', 'graphql', 'grpc', 'websocket', 'cli', 'auto']),
        default='auto'
    )

    if api_type == 'rest':
        framework = click.prompt(
            "⚡ Framework",
            type=click.Choice(['fastapi', 'flask']),
            default='fastapi'
        )
    else:
        framework = None

    output_name = click.prompt("📁 Nazwa projektu", default="", show_default=False)

    include_docker = click.confirm("🐳 Dołączyć pliki Docker?", default=True)
    include_tests = click.confirm("🧪 Wygenerować testy?", default=True)
    include_docs = click.confirm("📚 Wygenerować dokumentację?", default=True)

    # Podsumowanie
    table = Table(title="Podsumowanie konfiguracji")
    table.add_column("Opcja", style="cyan")
    table.add_column("Wartość", style="magenta")

    table.add_row("Opis", description[:50] + "...")
    table.add_row("Typ API", api_type)
    if framework:
        table.add_row("Framework", framework)
    table.add_row("Nazwa projektu", output_name or "auto")
    table.add_row("Docker", "✅" if include_docker else "❌")
    table.add_row("Testy", "✅" if include_tests else "❌")
    table.add_row("Dokumentacja", "✅" if include_docs else "❌")

    console.print(table)

    if click.confirm("\n🚀 Rozpocząć generowanie?"):
        # Wywołaj generate z parametrami
        args = [description]
        if output_name:
            args.extend(['--output', output_name])
        if api_type != 'auto':
            args.extend(['--type', api_type])
        if framework:
            args.extend(['--framework', framework])
        if not include_docker:
            args.append('--no-docker')
        if not include_tests:
            args.append('--no-tests')
        if not include_docs:
            args.append('--no-docs')

        from click.testing import CliRunner
        runner = CliRunner()
        runner.invoke(generate, args)


@cli.command()
def examples():
    """
    Pokazuje przykłady opisów do generowania API
    """

    console.print(Panel.fit(
        "📚 Przykłady opisów dla różnych typów API",
        title="Przykłady",
        border_style="green"
    ))

    for category, examples in SAMPLE_DESCRIPTIONS.items():
        console.print(f"\n🔸 {category.upper()}")

        for i, example in enumerate(examples, 1):
            console.print(f"  {i}. {example}")

    console.print("\n💡 Tip: Skopiuj przykład i użyj jako basis dla swojego API!")


@cli.command()
@click.option('--url', default='http://localhost:11434', help='URL serwera Ollama')
def check():
    """
    Sprawdza status narzędzi (Ollama, modele)
    """

    async def _check():
        console.print("🔍 Sprawdzam dostępność narzędzi...\n")

        # Sprawdź Ollama
        ollama_client = OllamaClient(base_url=url)

        with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
            task = progress.add_task("Sprawdzam Ollama...", total=None)

            ollama_ok = await ollama_client.health_check()
            progress.remove_task(task)

        # Status table
        table = Table(title="Status narzędzi")
        table.add_column("Komponent", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Uwagi", style="yellow")

        if ollama_ok:
            table.add_row("Ollama", "✅ Działa", f"URL: {url}")

            # Sprawdź modele
            try:
                models = await ollama_client.list_models()
                if models:
                    model_names = [m.name for m in models]
                    table.add_row("Modele", "✅ Dostępne", f"{len(models)} modeli")

                    console.print(table)
                    console.print(f"\n📋 Dostępne modele: {', '.join(model_names)}")

                    # Sprawdź czy jest llama3.1
                    recommended = ['llama3.1:8b', 'llama3.1:7b', 'llama3:8b']
                    available_recommended = [m for m in model_names if m in recommended]

                    if available_recommended:
                        console.print(f"✅ Zalecane modele dostępne: {', '.join(available_recommended)}")
                    else:
                        console.print("⚠️  Brak zalecanych modeli. Uruchom:")
                        console.print("   ollama pull llama3.1:8b")
                else:
                    table.add_row("Modele", "❌ Brak", "Pobierz model: ollama pull llama3.1:8b")
                    console.print(table)

            except Exception as e:
                console.print(f"[red]Błąd podczas sprawdzania modeli: {e}")
                console.print("[yellow]Upewnij się, że serwer Ollama jest uruchomiony i dostępny pod podanym adresem.")