# Blog API — Product Requirements Document (PRD)

Date: 2026-02-24

Owner: Project maintainer

Summary
- This PRD describes the FastAPI Blog API: goals, scope, API surface, data model alignment with the existing DB design, non-functional requirements, prioritized development roadmap, and explicit design decisions to confirm.

Project structure
- Project root (important files/folders):
  - `README.md` — project overview and setup notes
  - `requirements.txt` / `requirements-dev.txt` — dependencies
  - `alembic/` & `alembic.ini` — DB migrations scaffolding
  - `documentation/` — DB diagrams, data dictionary, and this PRD
  - `blogapi/` — main application package (contains `config.py`, `database.py`, `logging_conf.py`, `main.py`, `models/`, `routers/`, `tests/`)
  - `.env.example` — env var examples

- `blogapi/` layout (current important files):
  - `config.py` — Pydantic settings and environment-specific config
  - `database.py` — SQLAlchemy models, DB setup, and hooks (currently defines models and `create_all()` behavior)
  - `logging_conf.py` — structured logging config
  - `main.py` — application entrypoint (currently empty; to be scaffolded)
  - `models/` — (present, currently empty for per-module models). Pydantic models (request/response schemas) and domain DTOs. This folder will contain the Pydantic `schemas` used for validation and OpenAPI documentation; SQLAlchemy ORM models remain in `database.py` or may be moved into a separate `models/orm/` subpackage later.
  - `routers/` — (present, currently empty; will contain per-resource routers)
  - `tests/` — (present, currently empty; tests to be added using `pytest`)

This PRD assumes the above layout; implementation tasks will create missing routers, schemas, and CI configs inside these folders.

Objectives
- Provide a RESTful JSON API for a blog platform that supports posts, categories, tags, comments, attachments, revisions, and likes.
- Be production-ready (migrations, tests, CI) and easy to develop locally (sqlite/backends, local file storage).

Scope (In-scope)
- Core CRUD for Users, Posts, Categories, Tags.
- Authentication (signup/login) and protected write endpoints.
- Attachments upload and metadata persistence.
- Full-text search over posts (title + content) with pagination and filters.
- Threaded comments, revisions history, likes (per-user uniqueness).
- Alembic migrations, pytest tests, and a GitHub Actions CI pipeline.

Out of scope (initial)
- Social login (OAuth) — can be added later.
- Rich media processing (image resizing) — deferred to later iteration.

Data model mapping
- This API maps directly to the documented schema in `documentation/blog_data_dictionary.md` and `documentation/blog.dbml`:
  - `users`, `categories`, `posts`, `tags`, `post_tags`, `comments`, `attachments`, `revisions`, `likes`.
  - Posts will expose the searchable fields; `metadata` fields are treated as opaque JSON blobs and available for queries where required.

API Surface (summary)
- Authentication
  - POST /auth/register — register user
  - POST /auth/login — return access token
  - GET /auth/me — current user

- Users
  - GET /users/{id}
  - PATCH /users/{id}

- Posts
  - POST /posts — create (auth required)
  - GET /posts — list (filters: author, category, tags, status, q=search), pagination
  - GET /posts/{id} — retrieve
  - PATCH /posts/{id} — update (auth & author or admin)
  - DELETE /posts/{id} — soft-delete
  - POST /posts/{id}/revisions — snapshot
  - POST /posts/{id}/restore — rollback to revision

- Categories
  - CRUD: /categories

- Tags
  - CRUD: /tags

- Comments
  - POST /posts/{post_id}/comments — create (parent_id optional)
  - GET /posts/{post_id}/comments — list (threaded)
  - DELETE /comments/{id} — soft-delete

- Attachments
  - POST /attachments — upload multipart/form-data, returns URL + metadata
  - GET /attachments/{id}

- Likes
  - POST /likes — like a post/comment (enforce unique user+target)
  - DELETE /likes/{id}

Pagination and filtering
- Use query params `limit` and `offset` by default. Provide `page`/`per_page` helpers in SDK/docs.

Search
- Expose `GET /posts?q=...` backed by Postgres `tsvector` on `posts` (title + content) and a GIN index.

Non-functional requirements
- Tests: `pytest` unit and integration tests; use `TestConfig` (sqlite) and rollback behavior for DB tests.
- CI: GitHub Actions to run linters (`ruff`/`black`), `pytest`, and static checks on PRs.
- Migrations: use Alembic with an initial migration representing models and DB extension setup documented.
- Logging: structured logs via `blogapi/logging_conf.py`.

Security
- Passwords: hashed with `bcrypt` via `passlib` (or Argon2 later).
- Auth: JSON Web Tokens (JWT) for access tokens (short-life access + refresh token optional).
- Input validation: Pydantic models for all request/response shapes.
- Rate-limiting: document recommenders (e.g., API gateway) — not implemented in initial iteration.

Storage
- Local filesystem in development; Backblaze B2 in production (keys available in `config.py`).
- Attachments table stores `url`, `type`, `alt_text`, and `metadata`.

Migrations & DB
- Use Alembic for schema evolution. The initial migration will include required Postgres extensions:
  - `citext`, `pgcrypto` (or `uuid-ossp`), and `pg_trgm` where appropriate.
- Implement `posts.search` as a GENERATED STORED `tsvector` column: to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content,'')) and create a GIN index.

Testing
- Unit tests for services and routers using `pytest`.
- Integration tests use an ephemeral sqlite DB for speed and `DB_FORCE_ROLL_BACK` config for state isolation.

Roadmap (ordered, with milestones)
1) Scaffolding & infra
   - `main.py` FastAPI app, CORS, health endpoint, router registration
   - Logging and exception handlers
2) Schemas & Core CRUD
   - Pydantic `schemas.py` for requests/responses
   - CRUD routers for Posts, Users, Categories, Tags with pagination
3) Authentication
   - Password hashing, register/login, JWT issuance, `get_current_user` dependency
   - Protect write operations
4) Attachments & storage
   - Multipart upload endpoint, local and B2 adapters, persist metadata
5) Search & filtering
   - Implement `GET /posts?q=...`, filters (category, tags, author), pagination
6) Engagement features
   - Comments threading, revisions (create/list/rollback), likes API
7) Migrations & production readiness
   - Initial Alembic migration, document DB extensions and deployment steps
8) Tests & CI
   - Add pytest coverage for routers/services, GitHub Actions for lint/test
9) Docs & hardening
   - OpenAPI descriptions, example fixtures, rate-limiting, RBAC (optional)

Design decisions (proposed — please confirm)
- Auth: JSON Web Tokens (JWT) for access tokens. Rationale: simple, stateless, mobile-friendly. (DECIDED)
- Search column: Use a GENERATED STORED `tsvector` on `posts.search` populated from `title + content`. Rationale: keeps search logic in DB, fast with GIN index. (DECIDED)
- Storage: Support local filesystem for dev and Backblaze B2 in production. Rationale: local easier for dev; B2 offers inexpensive object storage. (DECIDED)
- UUID PKs & extensions: Use `pgcrypto` `gen_random_uuid()` for UUID default. Rationale: avoids uuid-ossp dependency in some environments. (DECIDED)
- Migrations: Use Alembic for all DB schema changes; avoid `create_all()` in production. (DECIDED)
- Tests: Use `pytest` + sqlite for quick tests and `DB_FORCE_ROLL_BACK` config for state isolation. (DECIDED)

Next actions
- I created this PRD file; please review and explicitly confirm or change the Design decisions marked "Proposed — confirm". After confirmation I will scaffold the app and implement the first milestone.

---
File generated and saved to repository documentation folder.
