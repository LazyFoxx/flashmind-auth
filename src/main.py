from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.infrastructure.db.db_helper import db_helper
from src.infrastructure.redis.client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await redis_client.get_client()
    yield
    # shutdown
    await redis_client.close()
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
