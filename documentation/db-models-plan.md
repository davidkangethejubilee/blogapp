# SQLAlchemy Core DB Models Plan

TL;DR — Implement Postgres-aligned SQLAlchemy Core `Table` definitions in `blogapi/database.py` from `documentation/blog.dbml`. Use Python `uuid.uuid4()` for IDs, `ON DELETE CASCADE` for FKs except `posts.category_id` (use `SET NULL`), and make `posts.search` a `TSVECTOR` GENERATED ALWAYS AS (to_tsvector('english', ...)) STORED; add GIN/JSONB indexes and DDL notes for Alembic.

## Steps
1. Update `blogapi/database.py` imports: add `import uuid`, `from sqlalchemy import Index, DDL, text`, and `from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR, CITEXT`.
2. Add DDL comments/snippets for required Postgres extensions: `citext`, `pg_trgm`, `pgcrypto` (place these in Alembic migrations).
3. Define SQLAlchemy Core `Table` objects for:
   - `users`, `categories`, `posts`, `tags`, `post_tags`, `comments`, `attachments`, `revisions`, `likes`.
4. Use `UUID(as_uuid=True)` for `id` columns with Python defaults: `default=uuid.uuid4`.
5. Foreign keys:
   - Use `ondelete="CASCADE"` for author→posts, posts→comments/attachments/revisions, comments→replies, likes→targets.
   - Use `ondelete="SET NULL"` for `posts.category_id`.
6. Create `posts.search` as a `TSVECTOR`:
   - `GENERATED ALWAYS AS (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content,'') || ' ' || coalesce(excerpt,''))) STORED`
   - Add a GIN index on `posts.search`.
7. Add JSONB `metadata` columns and GIN indexes; unique constraints for `email` and `slug`; composite UNIQUE on `(post_id, tag_id)` for `post_tags`; add recommended partial indexes `WHERE deleted_at IS NULL` where applicable.
8. Keep `database = Database(...)` and `metadata.create_all()` for local/dev usage; recommend Alembic for production migrations (place extension/index creation in migrations).
9. Add a small sanity test in `blogapi/tests/` that imports `blogapi.database` and verifies key tables/columns exist when run against a dev database.

## Implementation notes / Alembic
- Put extension creation in a migration, for example:
  - `CREATE EXTENSION IF NOT EXISTS citext;`
  - `CREATE EXTENSION IF NOT EXISTS pg_trgm;`
  - `CREATE EXTENSION IF NOT EXISTS pgcrypto;`
- Place index creation (GIN on `search` and JSONB `metadata`) and partial unique indexes in migrations.
- Note: PostgreSQL >= 12 (target is Postgres 18) is required for GENERATED ... STORED columns.

## Decisions already confirmed
- Target DB: PostgreSQL 18
- UUID generation: Python `uuid.uuid4()`
- FK policy: `ON DELETE CASCADE` except `posts.category_id` → `SET NULL`
- `search` language: `'english'` and implemented as `GENERATED ... STORED`

## Further considerations
- Use Alembic for production schema and extension DDL.
- Decide whether to generate UUIDs in DB later (if you prefer DB-side defaults, migrations must use `gen_random_uuid()`).
- Confirm any additional FK exceptions or column nullability adjustments before final implementation.

