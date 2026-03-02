# Coding Standards PRD: SQLAlchemy ORM + Pydantic + Async + Logging

Purpose
-------
This document defines the coding standards and conventions used across the project for database models (SQLAlchemy ORM, new 2.0 style), Pydantic (v2) schemas, asynchronous database access, and logging.

Scope
-----
- Backend Python services in this repository (all modules under blogapi/).
- Developers writing models, schemas, repositories, routers, and tests.

Stack & Versions
-----------------
- Python 3.10+
- SQLAlchemy 1.4+ / 2.0 style ORM (use the typed mapping helpers)
- Pydantic v2 (use `BaseModel` with `model_dump` / `model_validate`)
- Async DB: `AsyncEngine`, `AsyncSession`

Key Principles
--------------
- Prefer explicit, typed models and schemas. Use mypy-compatible type hints.
- Keep DB models and Pydantic schemas clearly separated: DB models for persistence, Pydantic for I/O/validation.
- Use async DB API consistently (no synchronous DB calls in request handlers).
- Use a repository/service layer (e.g., `PostRepository`) to encapsulate DB access and transactions.

SQLAlchemy ORM (new/2.0 style)
------------------------------
- Use declarative mapping with typed attributes: `Mapped`, `mapped_column` from `sqlalchemy.orm`.
- Define `__tablename__` and keep naming snake_case plural where appropriate.
- Use `Optional[...]` for nullable columns.
- Use explicit index/unique constraints via `mapped_column(...)` args or table-level constructs.

Example DB model (recommended style)

```py
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from blogapi.database import Base

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

```

Pydantic (v2) schemas
----------------------
- Use Pydantic v2 `BaseModel` for request/response models.
- Prefer `model_dump(exclude_unset=True)` when converting user input to dict for partial updates.

Example schema

```py
from pydantic import BaseModel

class UserPostIn(BaseModel):
    title: str
    content: str | None = None

    # use model_dump(exclude_unset=True) for updates

```

Project-specific examples (from this repo)
-----------------------------------------
Below are the concrete `Post` DB model and `UserPostIn` Pydantic schema taken from the codebase to illustrate the project's conventions.

`Post` model (excerpt from `blogapi/database.py`):

```py
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    author_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True), sqlalchemy.ForeignKey("categories.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    content: Mapped[Optional[str]] = mapped_column(Text)
    excerpt: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="draft"
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(sqlalchemy.DateTime)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    search: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        sqlalchemy.Computed(
            "to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content,'') || ' ' || coalesce(excerpt,''))",
            persisted=True,
        ),
    )
    created_at: Mapped[datetime] = mapped_column(
        sqlalchemy.DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        sqlalchemy.DateTime, onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sqlalchemy.DateTime)

```

`UserPostIn` schema (excerpt from `blogapi/models/schemas.py`):

```py
class UserPostIn(BaseModel):
    title: str = Field(..., example="My first post")
    content: Optional[str] = Field(None, example="Post body markdown/html")
    excerpt: Optional[str] = Field(None, example="Short summary")
    slug: Optional[str] = Field(None, example="my-first-post")
    category_id: Optional[UUID] = None
    metadata: Optional[dict] = None
    status: Optional[str] = Field(None, example="draft")
    author_id: UUID

```

Async DB usage
--------------
- Use `AsyncEngine` and `AsyncSession` everywhere; create sessions via dependency injection in routers.
- Use explicit commit/rollback patterns. Prefer using `async with session.begin():` when multiple statements are transactional.
- When updating ORM instances, mutate attributes and `await session.commit()`; call `await session.refresh(instance)` if you need canonical DB values (e.g., DB defaults, triggers, or refreshed columns).

Recommended repository pattern
------------------------------
- Keep DB access in repository classes (e.g., `PostRepository`).
- Repository methods should accept `AsyncSession` and return ORM instances or simple DTOs.
- Handle `IntegrityError` and roll back on exceptions. Do not swallow exceptions silently.

Soft-delete convention
----------------------
- Use `deleted_at` timestamp column to mark logical deletes instead of removing rows.
- Always filter queries with `Model.deleted_at.is_(None)` unless you explicitly need soft-deleted rows.

Logging
-------
- Use the centralized logging configuration (see logging_conf.py) to configure format and levels.
- Include structured fields where possible: `timestamp` (UTC), `level`, `module`, `request_id` (if available).
- Use named loggers (`logger = logging.getLogger(__name__)`) and appropriate levels.

Type hints and mypy
-------------------
- Annotate public functions and repository methods with return types (e.g., `-> Optional[Post]`).
- Use `from typing import Optional, List` consistently.

Testing & Migrations
--------------------
- Write unit tests for repository behaviors (create, update, soft_delete, listing filters).
- Use Alembic for schema migrations. Keep `alembic/` updated with migrations for model changes.

Code samples: commit / refresh pattern
-------------------------------------

```py
post.deleted_at = datetime.now(timezone.utc)
await session.commit()
await session.refresh(post)  # ensure instance reflects DB canonical values
return post
```

PR / Review checklist
---------------------
- DB models typed and use `mapped_column`/`Mapped`.
- Pydantic models used for I/O; no business logic in schemas.
- No sync DB calls in async handlers.
- Logging messages include context and appropriate log level.
- Tests updated and migrations added (if model changes are included).

Next steps
----------
- Adopt and review this PRD with the team.
- Apply automated linters / mypy and add CI checks to enforce conventions.
