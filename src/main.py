from fastapi import FastAPI
from contextlib import asynccontextmanager

from infrastructure.di.container import get_container
from dishka.integrations.fastapi import setup_dishka


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    container = get_container()
    app.state.dishka_container = container
    yield
    # shutdown
    await container.close()


app = FastAPI(lifespan=lifespan)
setup_dishka(get_container, app=app)
