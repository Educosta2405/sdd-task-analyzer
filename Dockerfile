# Imagem do Test Harness do TaskAnalyzer.
# Ambiente isolado e reprodutível: python:3.11-slim + dependências fixadas.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

# Dependências primeiro, para reaproveitar a camada em cache.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Apenas o necessário para executar os testes.
COPY pytest.ini .
COPY src/ src/
COPY tests/ tests/

# Executa sem privilégios de root.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

CMD ["pytest", "tests/test_harness.py", "-v"]
