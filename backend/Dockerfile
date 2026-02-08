# Estágio 1: Builder
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Otimizações do uv para Docker
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Instalar dependências primeiro (aproveitamento de cache do Docker)
COPY pyproject.toml /app/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    uv lock
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copiar o código fonte
COPY . .

# Sincronizar o projeto
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Estágio 2: Runtime
FROM python:3.12-slim-bookworm

# Variáveis de ambiente para Python em produção
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Criar um utilizador não-root por segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar apenas o ambiente virtual e o código do builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app /app

# Mudar para o utilizador não-root
USER appuser

# Expor a porta do FastAPI
EXPOSE 8000

# Comando de execução (usando o binário do venv diretamente)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
