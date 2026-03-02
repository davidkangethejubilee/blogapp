from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from blogapi.crud.posts import PostRepository
from blogapi.database import get_async_session
from blogapi.models.schemas import UserPost, UserPostIn

posts_router = APIRouter(prefix="/posts", tags=["posts"])


@posts_router.get("/", response_model=List[UserPost])
async def list_posts(
    skip: int = 0, limit: int = 20, session: AsyncSession = Depends(get_async_session)
):
    posts = await PostRepository.list(session, skip=skip, limit=limit)
    return [UserPost.model_validate(p) for p in posts]


@posts_router.post("/", response_model=UserPost, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: UserPostIn, session: AsyncSession = Depends(get_async_session)
):
    try:
        post = await PostRepository.create(session, post_in)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Post with that slug already exists"
        )
    return UserPost.model_validate(post)


@posts_router.get("/{post_id}", response_model=UserPost)
async def get_post(post_id: UUID, session: AsyncSession = Depends(get_async_session)):
    post = await PostRepository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return UserPost.model_validate(post)


@posts_router.put("/{post_id}", response_model=UserPost)
async def update_post(
    post_id: UUID,
    post_in: UserPostIn,
    session: AsyncSession = Depends(get_async_session),
):
    post = await PostRepository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    try:
        post = await PostRepository.update(session, post, post_in)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Update would violate constraints")
    return UserPost.model_validate(post)


@posts_router.delete("/{post_id}", response_model=UserPost)
async def delete_post(
    post_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    post = await PostRepository.get_by_id(session, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post = await PostRepository.soft_delete(session, post)
    return UserPost.model_validate(post)
