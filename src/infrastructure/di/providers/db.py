from typing import AsyncGenerator
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)
from src.core.settings.database import DatabaseSettings

from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.application.interfaces import AbstractUnitOfWork


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self, db_settings: DatabaseSettings) -> AsyncEngine:
        return create_async_engine(
            url=str(db_settings.get_url()),
            pool_size=db_settings.pool_size,
            max_overflow=db_settings.max_overflow,
            echo=db_settings.echo,
            pool_pre_ping=True,
            future=True,
        )

    @provide(scope=Scope.APP)
    def session_factory(
        self, engine: AsyncEngine
    ) -> "async_sessionmaker[AsyncSession]":
        return async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @provide(scope=Scope.REQUEST)
    def session(
        self, session_factory: "async_sessionmaker[AsyncSession]"
    ) -> AsyncSession:
        return session_factory()

    uow = provide(
        SqlAlchemyUnitOfWork,
        provides=AbstractUnitOfWork,
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.APP)
    async def engine_shutdown(self, engine: AsyncEngine) -> AsyncGenerator[None, None]:
        try:
            yield
        finally:
            await engine.dispose()
