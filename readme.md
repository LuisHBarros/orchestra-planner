🎼 Orchestra Planner
Orchestra Planner is a high-precision project management engine designed to orchestrate complex tasks with dynamic dependencies, automatic workload balancing, and native AI Agent integration.

Unlike generic "to-do" list applications, Orchestra Planner is built with Architectural Determinism at its core. It treats project management as a rigorous engineering problem, ensuring every schedule change is traceable, every transaction is atomic, and every AI interaction is grounded in strict domain rules.

🚀 Technology Stack
Language: Python 3.12+

Framework: FastAPI (Asynchronous, High-performance)

Database: PostgreSQL 16+ (Utilizing advanced ARRAY types for calendar management)

Dependency Manager: uv (Extremely fast Python package manager used for optimized builds)

Architecture: Hexagonal (Ports & Adapters)

Observability: structlog for JSON structured logging + Correlation IDs (X-Request-Id)

Infrastructure: Docker & Docker Compose (Multi-stage builds, non-root security)

🏗️ Architecture & Design Patterns
The project is built using Hexagonal Architecture, isolating the Domain Core from external concerns like databases, APIs, or LLM providers.

Design Patterns Implemented:
Unit of Work (UoW): Ensures transactional integrity across multiple repositories (e.g., firing a member and reassigning tasks is an "all-or-nothing" operation).

Policy Pattern: Centralizes business rule validation (e.g., TaskSelectionPolicy) to keep entities lean and testable.

Dependency Injection: Full decoupling of service orchestration via a centralized ContainerFactory.

Adapter Pattern: Pluggable infrastructure for LLM Providers and Notification services.

📋 Core Business Rules (BRs)
The system enforces strict domain logic defined in the code and ADRs:

BR-PROJ-002: Project Managers are administrative roles and cannot be assigned tasks.

BR-SCHED-003: The project schedule is automatically recalculated whenever dependencies, assignments, or task statuses change.

Seniority-Weighted Workload: Task completion time is dynamically adjusted based on the assigned member's seniority level and current workload capacity.

🧠 Hybrid LLM Strategy (BYOK)
Orchestra Planner supports a sophisticated Bring Your Own Key (BYOK) model:

Global House Model: A default, system-wide LLM (e.g., GPT-4o-mini or a local Ollama instance) for general features.

Project-Specific Override: Project owners can configure their own LLM providers and API keys, ensuring privacy and cost control at the project level.

Structured Outputs: All LLM responses are validated through Pydantic schemas before reaching the domain layer.

🛡️ Observability & SRE
Correlation IDs: Every request is assigned a unique X-Request-Id via middleware, which is propagated through all log entries and returned in response headers.

Structured Logging: Logs are emitted in JSON format, ready for immediate ingestion by Grafana Loki or ELK stacks.

Health Diagnostics: The /health endpoint performs real-time Readiness checks, verifying database connectivity and system state before accepting traffic.

📂 Architectural Decision Records (ADRs)
The evolution of this project is documented through 9 critical ADRs:

ADR 001: Hexagonal Architecture adoption.

ADR 002: PostgreSQL for ACID compliance in scheduling.

ADR 003: Manager-as-Member modeling strategy.

ADR 004: Centralized Schedule Recalculation architecture.

ADR 005: Transaction Safety via Unit of Work.

ADR 006: Rejection of HATEOAS in favor of the "Capabilities Pattern."

ADR 007: Passwordless Auth (Magic Links) & JWT Session management.

ADR 008: Structured Logging & Context Propagation.

ADR 009: Hybrid LLM Provider Resolution.

🛠️ Getting Started
Prerequisites
Docker & Docker Compose.

Quick Start
Bash
# Clone the repository
git clone https://github.com/luishbarros/orchestra-planner.git
cd orchestra-planner

# Start the entire stack (Database + API + Migrations)
docker-compose up --build
API: http://localhost:8000

Documentation: http://localhost:8000/docs (Swagger UI)

🗺️ Roadmap
Q2 2026: OpenTelemetry (OTEL) integration for distributed tracing.

Q3 2026: Real-time event-driven recalculation using a message broker (RabbitMQ/Redis).

Q4 2026: Advanced Gantt Chart visualization via a dedicated Frontend.
