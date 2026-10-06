FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Dependencias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalacao do uv e preparacao das dependencias
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Cria usuario sem privilegios de root para execucao segura
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appuser /app

# Copia codigo da aplicacao, compila arquivos estaticos e ajusta permissoes
COPY . .
RUN SECRET_KEY=build-time-static-key USE_SQLITE=True uv run python manage.py collectstatic --noinput && \
    chmod +x /app/docker/scripts/*.sh && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/docker/scripts/entrypoint.sh"]
CMD ["/app/docker/scripts/start-web.sh"]
