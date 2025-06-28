FROM python:3.11-slim

# Metadata
LABEL maintainer="text2api"
LABEL description="Automatyczne generowanie API z opisu tekstowego"
LABEL version="0.1.0"

# Argumenty budowania
ARG OLLAMA_URL=http://ollama:11434
ARG USER_ID=1000
ARG GROUP_ID=1000

# Zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV OLLAMA_URL=${OLLAMA_URL}
ENV GENERATED_APIS_DIR=/app/generated_apis

# Utwórz użytkownika niebędącego rootem
RUN groupadd -g ${GROUP_ID} text2api && \
    useradd -u ${USER_ID} -g text2api -m -s /bin/bash text2api

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki poetry
COPY pyproject.toml poetry.lock* ./

# Zainstaluj Poetry
RUN pip install poetry==1.6.1 && \
    poetry config virtualenvs.create false && \
    poetry install --only=main --no-root

# Skopiuj kod źródłowy
COPY text2api/ ./text2api/
COPY README.md ./

# Zainstaluj pakiet
RUN poetry install --only-root

# Utwórz katalogi dla wygenerowanych projektów
RUN mkdir -p ${GENERATED_APIS_DIR} && \
    chown -R text2api:text2api /app

# Przełącz na użytkownika text2api
USER text2api

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import text2api; print('OK')" || exit 1

# Domyślna komenda
ENTRYPOINT ["text2api"]
CMD ["--help"]

# Expose żadnych portów - to narzędzie CLI
# Volumy dla projektów
VOLUME ["/app/generated_apis"]