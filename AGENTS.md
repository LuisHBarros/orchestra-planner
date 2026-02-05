# Repository Guidelines

## Project Structure & Module Organization

- `backend/src/` contains the FastAPI app (`main.py`) and the Hexagonal Architecture layers:
  - `domain/` for core entities, errors, and ports (no external deps).
  - `application/use_cases/` for orchestration logic.
- `backend/tests/` mirrors domain and application tests.
- `docs/` and `business_rules.md` hold architecture notes and rule IDs referenced in errors.

## Build, Test, and Development Commands

- `source backend/venv/bin/activate` activates the Python venv used for local dev.
- `uvicorn backend.src.main:app --reload` runs the API with hot reload.
- `pytest` (run from `backend/`) executes the test suite using `backend/pytest.ini`.
- `curl http://localhost:8000/health` checks the health endpoint.

## Coding Style & Naming Conventions

- Python modules follow snake_case file names (e.g., `project_scheduler.py`).
- Tests use `test_*.py` files and `test_*` functions, consistent with `pytest.ini`.
- Keep domain code dependency-free; adapters should implement ports defined in `domain/ports/`.
- When adding rules or errors, reference `business_rules.md` IDs (e.g., `BR-TASK-003`).

## Testing Guidelines

- Framework: `pytest` with `asyncio_mode = auto` and `@pytest.mark.asyncio`.
- Unit tests should mock external ports; integration tests belong under adapters (if added).
- Add tests alongside the use case or service you touch, following existing patterns in
  `backend/tests/application/` and `backend/tests/domain/`.

## Commit & Pull Request Guidelines

- Commit messages follow Conventional Commits with optional scopes, for example:
  - `feat(project): add resign from project use case`
  - `refactor(task): add TaskSelectionPolicy`
- PRs should include:
  - A short description of the behavior change.
  - Links to related business rules or ADRs when applicable.
  - Notes on tests run (e.g., `pytest`).

## Architecture Notes

- Follow the implementation order in `CLAUDE.md` (domain → application → adapters).
- Keep dependencies flowing inward: adapters → application → domain.
