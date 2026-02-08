# ADR 002: Database Choice - PostgreSQL

- **Date:** 2026-01-31
- **Author:** luishbarros
- **Status:** accepted

## Context
The Orchestra Planner requires storing complex relational data:
- Projects, Tasks, Employees, Roles, and Workload calculations.
- Task dependencies (Finish-to-Start), dynamic project end dates, and constraints on task selection.
- Optional integration with LLM for difficulty estimation and progress calculations.
- Data integrity, transactions, and auditability are critical.

We need a database that supports **complex relationships, consistency, and maintainability**, while allowing flexibility for future scaling.

## Decision
Use **PostgreSQL** as the primary database for the Orchestra Planner.

Key points:
- Relational database with full ACID compliance.
- Supports complex queries, joins, and integrity constraints.
- Mature ecosystem, extensive documentation, and strong community support.
- Compatible with modular Hexagonal Architecture: adapters for repositories can abstract SQL details.

## Benefits
- **Data Integrity:** ACID transactions ensure consistency, especially for task dependencies and workload calculations.
- **Complex Relationships:** Relational model naturally handles Projects → Tasks → Employees → Roles.
- **Mature Ecosystem:** Rich tooling, libraries, and community support.
- **Scalability Options:** Can scale vertically and, with proper architecture, horizontally using partitioning or read replicas.
- **Integration:** Works smoothly with the Ports & Adapters approach (repository adapters can switch DB later if needed).

## Trade-offs
- **Learning Curve:** Team must be familiar with SQL and PostgreSQL-specific features.
- **Less Horizontal Flexibility than NoSQL:** Complex sharding or distributed setups require additional work.
- **Overhead for Simple Entities:** Some simple data structures could be stored more easily in a NoSQL DB.

## Alternatives
### MongoDB
Pros: Schema-less, flexible for unstructured data, easy horizontal scaling.
Cons: No full ACID transactions across multiple documents; harder to enforce relational integrity; complex queries can be slower and harder to optimize. Not ideal for task dependencies and workload calculations.

### MySQL
Pros: Widely known relational database, strong community, good performance for simpler relational workloads.
Cons: Less advanced features than PostgreSQL for complex queries, missing some advanced data types and concurrency features.

### Distributed SQL / NewSQL (e.g., CockroachDB, YugabyteDB)
Pros: Horizontal scalability, strong consistency.
Cons: Operational complexity, overkill for the current project size, requires additional setup and expertise.

## Consequences
- Domain adapters implement PostgreSQL-specific repository logic.
- Consistency is enforced for task dependencies, workload calculations, and project scheduling.
- Future migrations to other SQL databases remain feasible via repository ports.
- Developers must be trained on PostgreSQL features (transactions, constraints, joins, indexing).

## References
- PostgreSQL Documentation – https://www.postgresql.org/docs/
- SQL vs NoSQL Comparison – https://www.sitepoint.com/sql-vs-nosql-differences/
- ACID Transactions – https://en.wikipedia.org/wiki/ACID
