from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserPostIn(BaseModel):
    title: str = Field(..., example="My first post")
    content: Optional[str] = Field(None, example="Post body markdown/html")
    excerpt: Optional[str] = Field(None, example="Short summary")
    slug: Optional[str] = Field(None, example="my-first-post")
    category_id: Optional[UUID] = None
    metadata: Optional[dict] = None
    status: Optional[str] = Field(None, example="draft")
    author_id: UUID


class UserPost(UserPostIn):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
