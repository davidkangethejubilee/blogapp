from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from blogapi.database import Post
from blogapi.models.schemas import UserPostIn


class PostRepository:
    @staticmethod
    async def list(session: AsyncSession, skip: int = 0, limit: int = 20) -> List[Post]:
        stmt = select(Post).where(Post.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, post_id) -> Optional[Post]:
        stmt = select(Post).where(Post.id == post_id, Post.deleted_at.is_(None))
        result = await session.execute(stmt)
        return result.scalars().one_or_none()

    @staticmethod
    async def get_by_slug(session: AsyncSession, slug: str) -> Optional[Post]:
        stmt = select(Post).where(Post.slug == slug, Post.deleted_at.is_(None))
        result = await session.execute(stmt)
        return result.scalars().one_or_none()

    @staticmethod
    async def create(session: AsyncSession, post_in: UserPostIn) -> Post:
        post = Post(**post_in.model_dump(exclude_unset=True))
        session.add(post)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise
        await session.refresh(post)
        return post

    @staticmethod
    async def update(session: AsyncSession, post: Post, post_in: UserPostIn) -> Post:
        for k, v in post_in.model_dump(exclude_unset=True).items():
            setattr(post, k, v)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise
        await session.refresh(post)
        return post

    @staticmethod
    async def soft_delete(session: AsyncSession, post: Post) -> Post:
        post.deleted_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(post)
        return post
