# Optimized PRD Prompt

Use this prompt to generate a comprehensive Product Requirements Document (PRD) for the FastAPI Blog API and save it to `documentation/blog_api_prd.md` in the repository at:

`/home/davidk/Documents/Learning/Python/Dev with Copilot/blogapp`

---

## Project summary (use exactly)

- Tech stack: Python, FastAPI, PostgreSQL (dev: sqlite allowed for tests), pytest for unit tests.
- Repo root: `/home/davidk/Documents/Learning/Python/Dev with Copilot/blogapp`
- Primary package: `blogapi/`

### Current `blogapi/` structure to reference

- `blogapi/`
  - `config.py`
  - `database.py`
  - `logging_conf.py`
  - `main.py`
  - `models/`  — MUST contain Pydantic models (schemas) — state this explicitly
  - `routers/`
  - `tests/`

### DB schema references

- `documentation/blog.dbml` — use DBML contents; mention UUID PKs, `gen_random_uuid()`, `citext`, `pgcrypto`/UUID extension, `jsonb` metadata, `posts.search` `tsvector` + GIN index, and GENERATED/trigger note.
- `documentation/blog_data_dictionary.md` — use as data dictionary.

---

## Design decisions (CONFIRMED)

- Auth: JSON Web Tokens (JWT)
- Pydantic models live in `blogapi/models/`
- Unit tests use `pytest`
- Prioritize incremental, testable implementation with Alembic for migrations

---

## PRD requirements (produce as Markdown, saved to `documentation/blog_api_prd.md`)

The generated PRD must include the following sections and details:

1. Executive summary and goals.
2. Scope & non-goals.
3. API surface: list endpoints (CRUD) and example request/response shapes for Users, Posts, Categories, Tags, Comments, Attachments, Revisions, Likes; auth endpoints (signup/login/refresh) and protected routes; pagination and filtering conventions; error response format.
4. Data model summary referencing `documentation/blog.dbml` and `documentation/blog_data_dictionary.md`; call out Postgres-specific requirements (`citext`, `pgcrypto`/UUID, `pg_trgm`, GENERATED `tsvector` or trigger, GIN indexes).
5. Project structure section that exactly lists files/folders above and explicitly states `blogapi/models/` will contain Pydantic models (schemas) and `blogapi/routers/` will contain route modules.
6. Implementation roadmap (ordered, incremental priorities) — include these milestones in order:
   - Scaffolding: `main.py`, router registration, logging, health endpoint, CORS.
   - Database models & Pydantic schemas (`models/`): basic tables and CRUD repositories.
   - Auth (JWT): signup, login, token handling, `get_current_user` dependency, protect write routes.
   - Core CRUD endpoints: Posts, Users, Categories, Tags (with tests).
   - Attachments & storage (local dev + prod storage notes).
   - Search, filtering, pagination (use `posts.search` `tsvector` + GIN).
   - Comments, Revisions, Likes (business rules, uniqueness constraints).
   - Alembic migrations & DB extension setup.
   - Tests & CI: `pytest` tests, fixtures, GitHub Actions config to run tests.
   - Docs & hardening: OpenAPI/docs, rate limiting, RBAC notes.
7. Testing strategy: unit vs integration tests, test DB approach (sqlite or postgres test DB with transactional rollback), example `pytest` structure, coverage target.
8. Deliverables per milestone and acceptance criteria (APIs with tests passing, migrations present, CI green).
9. Next steps and TODOs (explicitly call out any decisions still needed).

---

## Formatting & output

- Use clear headings, bullet lists, and short actionable items.
- Include references/paths to `documentation/blog.dbml` and `documentation/blog_data_dictionary.md`.
- Save the final PRD Markdown to `documentation/blog_api_prd.md`.

---

## Final instruction for the assistant generating the PRD

Generate the PRD now and output only the file content (Markdown) suitable for writing to `documentation/blog_api_prd.md`.

The PRD must reference the repo and `blogapi/` structure above and mark the confirmed design decisions.

