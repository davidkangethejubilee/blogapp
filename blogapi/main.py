from contextlib import asynccontextmanager

from fastapi import FastAPI

from blogapi.database import database
from blogapi.routers.posts import posts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    try:
        yield
    finally:
        await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(posts_router)
