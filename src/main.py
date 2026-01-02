from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.infrastructure.db.db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)
