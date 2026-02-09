# 🎼 Orchestra Planner

**Orchestra Planner** is a high-precision project management engine designed to orchestrate complex tasks with dynamic dependencies, automatic workload balancing, and native AI Agent integration.

Unlike generic “to-do” list applications, Orchestra Planner is built with **Architectural Determinism** at its core. It treats project management as a rigorous engineering problem—ensuring that every schedule change is traceable, every transaction is atomic, and every AI interaction is grounded in strict domain rules.

---

## 🚀 Technology Stack

| Layer | Technology |
|------|------------|
| **Language** | Python 3.12+ |
| **API Framework** | FastAPI (async, high-performance) |
| **Database** | PostgreSQL 16+ (leveraging ARRAY types for calendar management) |
| **Package Manager** | `uv` (ultra-fast Python dependency resolver) |
| **Architecture** | Hexagonal (Ports & Adapters) |
| **Observability** | `structlog` with JSON logs + `X-Request-Id` correlation |
| **Infrastructure** | Docker & Docker Compose (multi-stage builds, non-root containers) |

---

## 🏗️ Architecture & Design Patterns

The system follows **Hexagonal Architecture**, keeping the **Domain Core** isolated from external concerns such as databases, APIs, or LLM providers.

### Design Patterns in Use

- **Unit of Work (UoW)**  
  Guarantees transactional integrity across repositories. Example: firing a team member and reassigning tasks happens atomically.

- **Policy Pattern**  
  Centralizes business validation (e.g., `TaskSelectionPolicy`), keeping entities clean and testable.

- **Dependency Injection**  
  All services are composed via a centralized `ContainerFactory`.

- **Adapter Pattern**  
  Pluggable integrations for LLM providers and notification services.

---

## 📋 Core Business Rules

Key domain constraints enforced by the system:

- **BR-PROJ-002** — Project Managers are administrative roles and cannot be assigned tasks.  
- **BR-SCHED-003** — The project schedule is automatically recalculated whenever dependencies, assignments, or task statuses change.  
- **Seniority-Weighted Workload** — Task duration dynamically adjusts based on member seniority and current capacity.

---

## 🧠 Hybrid LLM Strategy (BYOK)

Orchestra Planner supports a **Bring Your Own Key (BYOK)** model:

- **Global House Model**  
  A default system-wide LLM (e.g., GPT-4o-mini or local Ollama).

- **Project-Level Overrides**  
  Each project owner can configure their own LLM provider and API keys.

- **Structured Outputs**  
  All AI responses are validated with **Pydantic schemas** before entering the domain layer.

---

## 🛡️ Observability & SRE

- **Correlation IDs**  
  Every request gets an `X-Request-Id`, propagated through logs and responses.

- **Structured Logging**  
  JSON logs ready for **Grafana Loki** or **ELK**.

- **Health Checks**  
  `GET /health` performs readiness checks (DB connectivity + system state).

---

## 📂 Architectural Decision Records (ADRs)

The project’s evolution is documented via nine ADRs:

1. **ADR 001** — Hexagonal Architecture  
2. **ADR 002** — PostgreSQL for ACID scheduling  
3. **ADR 003** — Manager-as-Member modeling  
4. **ADR 004** — Centralized schedule recalculation  
5. **ADR 005** — Unit of Work transactions  
6. **ADR 006** — Capabilities Pattern over HATEOAS  
7. **ADR 007** — Passwordless Auth (Magic Links) + JWT  
8. **ADR 008** — Structured logging & context propagation  
9. **ADR 009** — Hybrid LLM resolution strategy  

---

## 🛠️ Getting Started

### Prerequisites

- Docker  
- Docker Compose  

### Quick Start

```bash
# Clone the repo
git clone https://github.com/luishbarros/orchestra-planner.git
cd orchestra-planner

# Start everything (DB + API + migrations)
docker-compose up --build
````

| Service               | URL                                                      |
| --------------------- | -------------------------------------------------------- |
| **API**               | [http://localhost:8000](http://localhost:8000)           |
| **Docs (Swagger UI)** | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

## 🗺️ Roadmap

* **Q2 2026** — OpenTelemetry (OTEL) distributed tracing
* **Q3 2026** — Event-driven recalculation (RabbitMQ / Redis)
* **Q4 2026** — Dedicated frontend with advanced Gantt charts

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a PR with clear motivation and tests where applicable.

---

## 📜 License

MIT License — feel free to use, modify, and build upon this project.

```
```
