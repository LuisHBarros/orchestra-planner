# Configuration

This document lists environment variables used for bootstrapping the API and
selecting service providers.

## Core

- `APP_ENV` (default: `local`)
  - Environment identifier (e.g., `local`, `staging`, `prod`).

- `DATABASE_URL` (required)
  - Async SQLAlchemy database URL.

## Service Provider Selection

Each provider can be set to `mock` (default) or a real provider name.
Real providers are currently stubs and will raise a clear error on use
until implemented.

- `EMAIL_PROVIDER` (default: `mock`)
- `TOKEN_PROVIDER` (default: `mock`)
- `ENCRYPTION_PROVIDER` (default: `mock`)
- `LLM_PROVIDER` (default: `mock`)
- `NOTIFICATION_PROVIDER` (default: `mock`)

## LLM (Global / House Model)

These are optional and used for the global LLM configuration. Projects still
configure their own provider + API key via `ConfigureProjectLLMUseCase`.

- `GLOBAL_LLM_API_KEY` (default: empty)
- `GLOBAL_LLM_BASE_URL` (default: empty)

## Examples

```bash
export APP_ENV=local
export DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/orchestra_planner
export EMAIL_PROVIDER=mock
export TOKEN_PROVIDER=mock
export ENCRYPTION_PROVIDER=mock
export LLM_PROVIDER=mock
export NOTIFICATION_PROVIDER=mock
```
