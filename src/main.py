from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.infrastructure.di.container import get_container
from dishka.integrations.fastapi import setup_dishka
from src.presentation.api.routers.router import api_router

container = get_container()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await container.close()


app = FastAPI(lifespan=lifespan)

setup_dishka(container, app=app)
app.include_router(api_router)
