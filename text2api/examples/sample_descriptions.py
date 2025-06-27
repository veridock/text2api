"""
Przykładowe opisy do demonstracji możliwości text2api
"""

SAMPLE_DESCRIPTIONS = {
    "rest_apis": [
        "API do zarządzania użytkownikami z operacjami CRUD, logowaniem i rejestracją",
        "System zarządzania produktami sklepu internetowego z kategoriami i cenami",
        "API dla systemu rezerwacji hoteli z pokojami, gośćmi i płatnościami",
        "Blog API z postami, komentarzami, tagami i autoryzacją użytkowników",
        "System zarządzania zadaniami (todo list) z projektami i terminami",
        "API dla biblioteki z książkami, wypożyczeniami i czytelnikami",
        "System fakturowania z klientami, fakturami i pozycjami",
        "API dla platformy e-learning z kursami, lekcjami i studentami",
        "System zarządzania wydarzeniami z terminarzem i uczestnikami",
        "API dla aplikacji fitness z treningami, ćwiczeniami i statystykami",
    ],
    "graphql_apis": [
        "GraphQL API dla mediów społecznościowych z postami, komentarzami i relacjami",
        "System zarządzania treścią (CMS) z artykułami, kategoriami i autorami",
        "API dla platformy streamingowej z filmami, serialami i ocenami",
        "System zarządzania projektami z zadaniami, zespołami i milestone'ami",
        "GraphQL dla sklepu z produktami, kategoriami, zamówieniami i recenzjami",
        "API dla platformy edukacyjnej z kursami, modułami i postępami studentów",
    ],
    "grpc_apis": [
        "Mikrousługa do przetwarzania płatności z walidacją i powiadomieniami",
        "Serwis uwierzytelniania z tokenami JWT i odświeżaniem sesji",
        "API do konwersji walut z aktualnymi kursami i historią",
        "Mikrousługa do wysyłki emaili z szablonami i kolejką",
        "Serwis geolokalizacji z wyszukiwaniem miejscowości i dystansów",
        "API do analizy sentimentu tekstu z wynikami i statystykami",
    ],
    "websocket_apis": [
        "Serwer czatu w czasie rzeczywistym z pokojami i historią wiadomości",
        "System notyfikacji push z subskrypcjami i filtrami",
        "API do gier wieloosobowych z synchronizacją stanu gry",
        "Platforma streamingu danych finansowych z kursami giełdowymi",
        "System monitoringu IoT z czujnikami i alertami w czasie rzeczywistym",
        "Kolaboracyjny edytor tekstu z synchronizacją zmian między użytkownikami",
    ],
    "cli_tools": [
        "Narzędzie do konwersji plików między formatami (JSON, XML, CSV, YAML)",
        "CLI do zarządzania bazą danych z migracjami i backupami",
        "Generator dokumentacji z kodu źródłowego z różnymi formatami wyjściowymi",
        "Narzędzie do optymalizacji obrazów z batch processingiem",
        "CLI do deploymentu aplikacji na różne platformy chmurowe",
        "Analizator logów z filtrowaniem, statystykami i raportami",
        "Generator projektów z templates i konfiguracją",
        "Narzędzie do testowania API z assertions i raportami",
        "CLI do zarządzania secrets i konfiguracją środowisk",
        "Backup tool z kompresją, szyfrowaniem i harmonogramem",
    ],
    "complex_examples": [
        """
        Kompletny system e-commerce z następującymi funkcjonalnościami:
        - Zarządzanie produktami z kategoriami, wariantami i zdjęciami
        - Koszyk zakupowy z sesją i zapisywaniem stanu
        - System płatności z różnymi metodami i fakturowaniem
        - Zarządzanie zamówieniami ze statusami i śledzeniem
        - System użytkowników z rolami (klient, admin, sprzedawca)
        - Recenzje i oceny produktów
        - System promocji i kodów rabatowych
        - Powiadomienia email o statusie zamówienia
        - Panel administracyjny z raportami sprzedaży
        - API dla aplikacji mobilnej
        """,
        """
        Platforma do zarządzania projektami z funkcjami:
        - Tworzenie projektów z zespołami i uprawnieniami
        - Zarządzanie zadaniami z priorytetami i terminami
        - System komentarzy i załączników do zadań
        - Śledzenie czasu pracy z timetrackingiem
        - Kalendarz z milestone'ami i spotkaniami
        - Generowanie raportów i dashboardów
        - Integracje z Git i narzędziami CI/CD
        - Powiadomienia w czasie rzeczywistym
        - API dla integracji z zewnętrznymi narzędziami
        - System fakturowania czasu pracy
        """,
        """
        System zarządzania uczelnią z modułami:
        - Zarządzanie studentami z danymi osobowymi i akademickimi
        - System kursów z planami studiów i przedmiotami
        - Zapisy na zajęcia z limitami miejsc
        - Oceny i egzaminy z różnymi systemami punktacji
        - Harmonogram zajęć dla studentów i wykładowców
        - Biblioteka z katalogiem książek i wypożyczeniami
        - System płatności czesnego i opłat
        - Portal dla studentów i wykładowców
        - Generowanie dyplomów i zaświadczeń
        - Statystyki i raporty akademickie
        """,
    ],
    "polish_examples": [
        "API do systemu kolejkowego w urzędzie z numerkami i powiadomieniami",
        "System rezerwacji sal konferencyjnych z kalendarzem i dostępnością",
        "API dla aplikacji dostaw jedzenia z restauracjami i kurierami",
        "System zarządzania flotą pojazdów z GPS i konserwacją",
        "API do systemu parkingowego z miejscami i opłatami",
        "Platform do nauki języków z lekcjami, ćwiczeniami i postępami",
        "System elektronicznych recept z lekarzami i aptekami",
        "API dla systemu głosowania elektronicznego z kandydatami",
        "Platforma crowdfundingowa z projektami i wpłatami",
        "System zarządzania odpadami z harmonogramem wywozu",
    ],
    "international_examples": [
        "Multi-tenant SaaS platform for customer relationship management",
        "Real-time collaboration platform for distributed teams",
        "IoT data collection and analytics platform with dashboards",
        "Content delivery network (CDN) management API",
        "Machine learning model serving platform with versioning",
        "Digital asset management system for creative teams",
        "API for cryptocurrency trading with real-time market data",
        "Logistics and supply chain management platform",
        "Healthcare patient management system with appointments",
        "Smart city infrastructure monitoring platform",
    ],
}


def get_random_description(category: str = None) -> str:
    """
    Zwraca losowy przykład opisu

    Args:
        category: Kategoria przykładu lub None dla losowego

    Returns:
        Przykładowy opis
    """
    import random

    if category and category in SAMPLE_DESCRIPTIONS:
        return random.choice(SAMPLE_DESCRIPTIONS[category])

    # Losowy z wszystkich kategorii
    all_examples = []
    for examples in SAMPLE_DESCRIPTIONS.values():
        all_examples.extend(examples)

    return random.choice(all_examples)


def get_examples_by_complexity(simple: bool = True) -> list:
    """
    Zwraca przykłady według poziomu złożoności

    Args:
        simple: True dla prostych przykładów, False dla złożonych

    Returns:
        Lista przykładów
    """

    if simple:
        simple_categories = ["rest_apis", "cli_tools", "polish_examples"]
        examples = []
        for cat in simple_categories:
            examples.extend(SAMPLE_DESCRIPTIONS[cat][:3])  # Po 3 z każdej kategorii
        return examples
    else:
        return SAMPLE_DESCRIPTIONS["complex_examples"]


def get_examples_by_api_type(api_type: str) -> list:
    """
    Zwraca przykłady dla konkretnego typu API

    Args:
        api_type: rest, graphql, grpc, websocket, cli

    Returns:
        Lista przykładów dla danego typu
    """

    type_mapping = {
        "rest": "rest_apis",
        "graphql": "graphql_apis",
        "grpc": "grpc_apis",
        "websocket": "websocket_apis",
        "cli": "cli_tools",
    }

    category = type_mapping.get(api_type)
    if category:
        return SAMPLE_DESCRIPTIONS[category]

    return []


def search_examples(query: str) -> list:
    """
    Wyszukuje przykłady zawierające dane słowa kluczowe

    Args:
        query: Zapytanie do wyszukiwania

    Returns:
        Lista pasujących przykładów
    """

    query_lower = query.lower()
    matching = []

    for category, examples in SAMPLE_DESCRIPTIONS.items():
        for example in examples:
            if query_lower in example.lower():
                matching.append((category, example))

    return matching


# Przykłady dla różnych poziomów zaawansowania użytkownika
BEGINNER_EXAMPLES = [
    "Proste API do listy zadań z dodawaniem, edycją i usuwaniem",
    "API dla książki adresowej z kontaktami",
    "System logowania użytkowników z rejestracją",
    "API do zarządzania notatkami z tagami",
    "Prosta aplikacja do głosowania z opcjami",
]

INTERMEDIATE_EXAMPLES = [
    "Blog z systemem komentarzy, tagów i kategorii",
    "E-commerce z produktami, koszykiem i płatnościami",
    "System zarządzania pracownikami z działami",
    "API dla aplikacji pogodowej z prognozami",
    "Platforma do udostępniania plików z folderami",
]

ADVANCED_EXAMPLES = [
    "Mikrousługi dla bankowości z transakcjami i bezpieczeństwem",
    "Real-time gaming API z matchmakingiem i ranking",
    "ML platform z modelami, treningiem i predykcjami",
    "IoT management system z devices i telemetrią",
    "Multi-tenant SaaS z billing i analytics",
]


def get_examples_by_skill_level(level: str) -> list:
    """
    Zwraca przykłady według poziomu umiejętności

    Args:
        level: beginner, intermediate, advanced

    Returns:
        Lista przykładów
    """

    level_mapping = {
        "beginner": BEGINNER_EXAMPLES,
        "intermediate": INTERMEDIATE_EXAMPLES,
        "advanced": ADVANCED_EXAMPLES,
    }

    return level_mapping.get(level, BEGINNER_EXAMPLES)
