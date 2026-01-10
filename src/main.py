from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.infrastructure.di.container import get_container
from dishka.integrations.fastapi import setup_dishka
from src.presentation.exception_handlers import setup_exception_handlers
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
setup_exception_handlers(app)

app.include_router(api_router)
