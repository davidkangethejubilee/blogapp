import uuid
from datetime import datetime
from typing import Optional

import databases
import sqlalchemy
from sqlalchemy import DDL, Index, String, Text, event
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from blogapi.config import config


# Extension DDL (kept here for local/dev `create_all`, but prefer Alembic for production)
create_citext = DDL("CREATE EXTENSION IF NOT EXISTS citext;")
create_pg_trgm = DDL("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
create_pgcrypto = DDL("CREATE EXTENSION IF NOT EXISTS pgcrypto;")


# Declarative Base for ORM models
class Base(DeclarativeBase):
    pass


# Users
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(Text)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(sqlalchemy.DateTime, onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sqlalchemy.DateTime)


# Categories
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, server_default=func.now(), nullable=False)


# Posts
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("categories.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    content: Mapped[Optional[str]] = mapped_column(Text)
    excerpt: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")
    published_at: Mapped[Optional[datetime]] = mapped_column(sqlalchemy.DateTime)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    search: Mapped[Optional[str]] = mapped_column(
        TSVECTOR,
        sqlalchemy.Computed(
            "to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content,'') || ' ' || coalesce(excerpt,''))",
            persisted=True,
        ),
    )
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(sqlalchemy.DateTime, onupdate=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sqlalchemy.DateTime)


# Tags
class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, server_default=func.now(), nullable=False)


# Post_Tags (many-to-many association)
class PostTag(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, server_default=func.now(), nullable=False)


# Comments (threaded via parent_id)
class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"))
    parent_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("comments.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, server_default=func.now(), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(sqlalchemy.DateTime)


# Attachments
class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("posts.id", ondelete="CASCADE"))
    uploader_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    alt_text: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, server_default=func.now(), nullable=False)


# Revisions
class Revision(Base):
    __tablename__ = "revisions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    editor_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, server_default=func.now(), nullable=False)


# Likes (polymorphic target)
class Like(Base):
    __tablename__ = "likes"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(sqlalchemy.DateTime, server_default=func.now(), nullable=False)


# Get metadata from Base for use with engine.create_all()
metadata = Base.metadata

# Indexes and constraints
# Unique constraints for email and slugs (with partial index to ignore soft-deleted rows)
Index("uq_users_email", User.email, unique=True, postgresql_where=sqlalchemy.text("deleted_at IS NULL"))
Index("uq_posts_slug_active", Post.slug, unique=True, postgresql_where=sqlalchemy.text("deleted_at IS NULL"))

# GIN index on posts.search and JSONB metadata
Index("ix_posts_search", Post.search, postgresql_using="gin")
Index("ix_posts_metadata_gin", Post.metadata, postgresql_using="gin")


# Attach DDL to metadata so extensions are created when using metadata.create_all (dev only)
event.listen(metadata, "before_create", create_citext)
event.listen(metadata, "before_create", create_pg_trgm)
event.listen(metadata, "before_create", create_pgcrypto)


# Note: "check_same_thread" is only needed for SQLite, not for PostgreSQL
connect_args = {"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
engine = sqlalchemy.create_engine(config.DATABASE_URL, connect_args=connect_args)


metadata.create_all(engine)
db_args = {"min_size": 1, "max_size": 3} if "postgres" in config.DATABASE_URL else {}
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLL_BACK, **db_args
)

