╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Plan to implement                                                                                                                   │
│                                                                                                                                     │
│ Plan: Fix All 10 Backend Gaps                                                                                                       │
│                                                                                                                                     │
│ Context                                                                                                                             │
│                                                                                                                                     │
│ Analysis of the Orchestra Planner backend revealed 10 gaps ranging from quick config fixes to missing features. This plan addresses │
│  all of them in dependency order, quick wins first.                                                                                 │
│                                                                                                                                     │
│ ---                                                                                                                                 │
│ Phase 1 — Quick Wins (3 items)                                                                                                      │
│                                                                                                                                     │
│ 1.1 Fix echo=True in session.py                                                                                                     │
│                                                                                                                                     │
│ File: backend/src/infrastructure/db/session.py (line 28)                                                                            │
│                                                                                                                                     │
│ - Make echo conditional on env: echo=os.getenv("DB_ECHO", "false").lower() == "true"                                                │
│ - The module-level engine = create_db_engine() at line 35 runs at import time, so the env var approach is simplest                  │
│                                                                                                                                     │
│ 1.2 Fix Python version mismatch in CLAUDE.md                                                                                        │
│                                                                                                                                     │
│ File: CLAUDE.md                                                                                                                     │
│                                                                                                                                     │
│ - Change "Python: 3.14+" to "Python: 3.12+" — pyproject.toml and Dockerfile both use 3.12, which is the truth                       │
│                                                                                                                                     │
│ 1.3 Remove empty ProjectScheduler stub                                                                                              │
│                                                                                                                                     │
│ Files to delete:                                                                                                                    │
│ - backend/src/domain/services/project_scheduler.py (empty 1-line file)                                                              │
│ - backend/tests/domain/services/test_project_scheduler.py (empty 1-line file)                                                       │
│                                                                                                                                     │
│ ScheduleCalculator already handles all scheduling. RecalculateProjectScheduleUseCase orchestrates it. There's no distinct role for  │
│ a separate service. Remove any references from __init__.py exports.                                                                 │
│                                                                                                                                     │
│ ---                                                                                                                                 │
│ Phase 2 — Small Fixes (2 items)                                                                                                     │
│                                                                                                                                     │
│ 2.1 Verify Alembic setup                                                                                                            │
│                                                                                                                                     │
│ Alembic files do exist: backend/alembic/versions/001_initial.py, env.py, script.py.mako. The gap was incorrectly flagged.           │
│                                                                                                                                     │
│ Action: Verify docker-compose.yaml migrations service command runs from the correct working directory. The Dockerfile uses WORKDIR  │
│ /app and copies everything, so alembic.ini should be accessible. May need to adjust the command path.                               │
│                                                                                                                                     │
│ 2.2 Add email format validation to auth router                                                                                      │
│                                                                                                                                     │
│ File: backend/src/adapters/api/routers/auth.py (line 19)                                                                            │
│                                                                                                                                     │
│ - MagicLinkRequest.email uses str with min_length=3 but no email format validation                                                  │
│ - Change to EmailStr from pydantic or add a @field_validator with regex                                                             │
│                                                                                                                                     │
│ ---                                                                                                                                 │
│ Phase 3 — RecalculateSchedule → UoW Refactor                                                                                        │
│                                                                                                                                     │
│ 3.1 Make RecalculateProjectScheduleUseCase transactional                                                                            │
│                                                                                                                                     │
│ Files:                                                                                                                              │
│ - backend/src/application/use_cases/project_management/recalculate_project_schedule.py — replace 4 individual repo params with      │
│ UnitOfWork + ScheduleCalculator                                                                                                     │
│ - backend/src/infrastructure/di.py — update recalculate_project_schedule_use_case() factory to pass self.uow +                      │
│ self.domain_services.schedule_calculator                                                                                            │
│ - backend/tests/application/project_management/test_recalculate_project_schedule.py — refactor to UoW mock pattern (match           │
│ test_fire_employee.py style)                                                                                                        │
│                                                                                                                                     │
│ Approach:                                                                                                                           │
│ class RecalculateProjectScheduleUseCase:                                                                                            │
│     def __init__(self, uow: UnitOfWork, schedule_calculator: ScheduleCalculator):                                                   │
│         self.uow = uow                                                                                                              │
│         self.schedule_calculator = schedule_calculator                                                                              │
│                                                                                                                                     │
│     async def execute(self, input):                                                                                                 │
│         async with self.uow as uow:                                                                                                 │
│             tasks = await uow.task_repository.find_by_project(...)                                                                  │
│             deps = await uow.task_dependency_repository.find_by_project(...)                                                        │
│             members = await uow.project_member_repository.find_by_project(...)                                                      │
│             project = await uow.project_repository.find_by_id(...)                                                                  │
│             # ... calculate + update tasks ...                                                                                      │
│             if tasks_to_save:                                                                                                       │
│                 await uow.task_repository.save_many(tasks_to_save)                                                                  │
│                 await uow.commit()                                                                                                  │
│             return schedule                                                                                                         │
│                                                                                                                                     │
│ ---                                                                                                                                 │
│ Phase 4 — Auth Flow (wire JWT tokens)                                                                                               │
│                                                                                                                                     │
│ 4.1 Update VerifyMagicLinkUseCase to issue tokens                                                                                   │
│                                                                                                                                     │
│ Files:                                                                                                                              │
│ - backend/src/application/use_cases/auth/verify_magic_link.py — add TokenService dependency, return VerifyMagicLinkOutput(user,     │
│ token_pair) instead of just User                                                                                                    │
│ - backend/src/infrastructure/di.py — pass self.services.token to verify use case                                                    │
│                                                                                                                                     │
│ 4.2 Update auth router to return tokens                                                                                             │
│                                                                                                                                     │
│ File: backend/src/adapters/api/routers/auth.py                                                                                      │
│ - Add access_token, refresh_token, token_type to VerifyMagicLinkResponse                                                            │
│ - Add POST /auth/refresh and POST /auth/revoke endpoints                                                                            │
│                                                                                                                                     │
│ 4.3 Implement JWT-based CurrentUserIdProvider                                                                                       │
│                                                                                                                                     │
│ File: backend/src/adapters/api/deps.py or new backend/src/adapters/api/auth_provider.py                                             │
│                                                                                                                                     │
│ - Extract Authorization: Bearer <token> header                                                                                      │
│ - Call token_service.verify_token(token) to validate                                                                                │
│ - Extract user_id from claims                                                                                                       │
│ - Raise HTTPException(401) if invalid                                                                                               │
│                                                                                                                                     │
│ 4.4 Replace DenyAllCurrentUserProvider                                                                                              │
│                                                                                                                                     │
│ Files:                                                                                                                              │
│ - backend/src/adapters/api/routers/common.py — rewrite get_current_user_id() as a proper FastAPI dependency that creates the JWT    │
│ provider using the token service from ContainerFactory                                                                              │
│ - backend/src/app_factory.py — remove DenyAllCurrentUserProvider registration (line 130), store token service reference in deps     │
│ module instead                                                                                                                      │
│                                                                                                                                     │
│ 4.5 Update tests                                                                                                                    │
│                                                                                                                                     │
│ File: backend/tests/application/auth/test_verify_magic_link.py — mock TokenService, assert token pair returned                      │
│                                                                                                                                     │
│ ---                                                                                                                                 │
│ Phase 5 — Real Service Implementations                                                                                              │
│                                                                                                                                     │
│ 5.1 Create new service adapter files                                                                                                │
│                                                                                                                                     │
│ Each implements the corresponding port Protocol:                                                                                    │
│ ┌─────────────────────────────────────────────────┬─────────────────────┬──────────────────────────┐                                │
│ │                 File to Create                  │     Implements      │         Library          │                                │
│ ├─────────────────────────────────────────────────┼─────────────────────┼──────────────────────────┤                                │
│ │ adapters/services/jwt_token_service.py          │ TokenService        │ PyJWT                    │                                │
│ ├─────────────────────────────────────────────────┼─────────────────────┼──────────────────────────┤                                │
│ │ adapters/services/smtp_email_service.py         │ EmailService        │ aiosmtplib               │                                │
│ ├─────────────────────────────────────────────────┼─────────────────────┼──────────────────────────┤                                │
│ │ adapters/services/fernet_encryption_service.py  │ EncryptionService   │ cryptography             │                                │
│ ├─────────────────────────────────────────────────┼─────────────────────┼──────────────────────────┤                                │
│ │ adapters/services/openai_llm_service.py         │ LLMService          │ openai                   │                                │
│ ├─────────────────────────────────────────────────┼─────────────────────┼──────────────────────────┤                                │
│ │ adapters/services/email_notification_service.py │ NotificationService │ Composes on EmailService │                                │
│ └─────────────────────────────────────────────────┴─────────────────────┴──────────────────────────┘                                │
│ 5.2 Add settings                                                                                                                    │
│                                                                                                                                     │
│ File: backend/src/config/settings.py — add fields:                                                                                  │
│ - JWT: jwt_secret_key, jwt_algorithm, access_token_expiry_minutes, refresh_token_expiry_minutes                                     │
│ - SMTP: smtp_host, smtp_port, smtp_user, smtp_password, smtp_from_email, smtp_use_tls                                               │
│ - Encryption: encryption_key                                                                                                        │
│ - LLM: llm_model                                                                                                                    │
│                                                                                                                                     │
│ 5.3 Wire in app_factory.py                                                                                                          │
│                                                                                                                                     │
│ File: backend/src/app_factory.py — replace Real*Stub classes with real implementations based on provider settings (e.g.,            │
│ token_provider == "jwt" → JWTTokenService)                                                                                          │
│                                                                                                                                     │
│ 5.4 Add dependencies to pyproject.toml                                                                                              │
│                                                                                                                                     │
│ PyJWT>=2.8, cryptography>=41.0, aiosmtplib>=3.0, openai>=1.10                                                                       │
│                                                                                                                                     │
│ ---                                                                                                                                 │
│ Phase 6 — Missing Use Cases                                                                                                         │
│                                                                                                                                     │
│ 6.1 New use cases to implement                                                                                                      │
│ Use Case: DeleteTask                                                                                                                │
│ File: application/use_cases/task_management/delete_task.py                                                                          │
│ Pattern: UoW                                                                                                                        │
│ Key Logic: Manager-only, delete deps referencing task                                                                               │
│ ────────────────────────────────────────                                                                                            │
│ Use Case: CancelTask                                                                                                                │
│ File: application/use_cases/task_management/cancel_task.py                                                                          │
│ Pattern: Repos                                                                                                                      │
│ Key Logic: Manager-only, TODO→CANCELLED via task.cancel()                                                                           │
│ ────────────────────────────────────────                                                                                            │
│ Use Case: AddDependency                                                                                                             │
│ File: application/use_cases/task_management/add_dependency.py                                                                       │
│ Pattern: UoW                                                                                                                        │
│ Key Logic: Cycle detection via detect_circular_dependency(), auto-block child if parent not DONE                                    │
│ ────────────────────────────────────────                                                                                            │
│ Use Case: RemoveDependency                                                                                                          │
│ File: application/use_cases/task_management/remove_dependency.py                                                                    │
│ Pattern: UoW                                                                                                                        │
│ Key Logic: Check if blocked task can be unblocked                                                                                   │
│ ────────────────────────────────────────                                                                                            │
│ Use Case: ConfigureCalendar                                                                                                         │
│ File: application/use_cases/project_management/configure_calendar.py                                                                │
│ Pattern: Repos                                                                                                                      │
│ Key Logic: Uses CalendarRepository, triggers schedule recalculation                                                                 │
│ 6.2 Wire into DI + API                                                                                                              │
│                                                                                                                                     │
│ - Add factory methods to Container in backend/src/infrastructure/di.py                                                              │
│ - Add CalendarRepository to Repositories dataclass (it's a port but never wired)                                                    │
│ - Add API endpoints to existing routers (tasks.py, projects.py)                                                                     │
│ - Notification use cases deferred — require background task infrastructure (separate ADR)                                           │
│                                                                                                                                     │
│ 6.3 Tests for each new use case                                                                                                     │
│                                                                                                                                     │
│ One test file per use case following existing patterns: @pytest.mark.asyncio, AsyncMock for ports, fixture-based setup.             │
│                                                                                                                                     │
│ ---                                                                                                                                 │
│ Phase 7 — Integration Tests                                                                                                         │
│                                                                                                                                     │
│ 7.1 Test infrastructure                                                                                                             │
│                                                                                                                                     │
│ Files to create:                                                                                                                    │
│ - backend/tests/conftest.py — test DB engine, session fixture with per-test rollback                                                │
│ - backend/tests/integration/conftest.py — DB-specific fixtures                                                                      │
│                                                                                                                                     │
│ Setup: Test DB via TEST_DATABASE_URL env var, Base.metadata.create_all for schema, rollback after each test for isolation.          │
│                                                                                                                                     │
│ 7.2 Repository integration tests (9 files)                                                                                          │
│                                                                                                                                     │
│ backend/tests/integration/db/test_<entity>_repository.py for each of the 9 repository adapters.                                     │
│                                                                                                                                     │
│ Pattern: instantiate Postgres*Repository(session), exercise CRUD, verify entity round-trip.                                         │
│                                                                                                                                     │
│ 7.3 API integration tests (6 files)                                                                                                 │
│                                                                                                                                     │
│ backend/tests/integration/api/test_<router>_endpoints.py using httpx.AsyncClient with ASGITransport(app).                           │
│                                                                                                                                     │
│ Pattern: create app with test overrides, send HTTP requests, assert status codes and response bodies.                               │
│                                                                                                                                     │
│ 7.4 Add test dependencies                                                                                                           │
│                                                                                                                                     │
│ File: backend/pyproject.toml — add httpx>=0.27 to test dependencies.                                                                │
│                                                                                                                                     │
│ ---                                                                                                                                 │
│ Verification                                                                                                                        │
│                                                                                                                                     │
│ After all phases:                                                                                                                   │
│ 1. cd backend && pytest — all existing + new unit tests pass                                                                        │
│ 2. cd backend && pytest tests/integration/ — integration tests pass (requires test DB)                                              │
│ 3. Manual flow: POST /auth/magic-link → GET /debug/last-magic-link → POST /auth/verify → get JWT → use Bearer token on protected    │
│ endpoints                                                                                                                           │
│ 4. docker compose up — app starts, health check returns {"liveness": "ok", "readiness": {"db": "ok"}
