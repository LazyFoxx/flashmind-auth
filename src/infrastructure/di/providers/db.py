from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)
from infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.application.interfaces import AbstractUnitOfWork


class DbProvider(Provider):
    # Engine — singleton
    engine = provide(
        lambda db_settings: create_async_engine(
            url=db_settings.get_url(),
            pool_size=db_settings.pool_size,
            max_overflow=db_settings.max_overflow,
            echo=db_settings.echo,
            pool_pre_ping=True,
            future=True,
        ),
        provides=AsyncEngine,
        scope=Scope.APP,
    )

    session_factory = provide(
        lambda engine: async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            class_=AsyncSession,
        ),
        scope=Scope.APP,
    )

    session = provide(
        lambda session_factory: session_factory(),
        provides=AsyncSession,
        scope=Scope.REQUEST,
    )

    uow = provide(
        SqlAlchemyUnitOfWork,
        provides=AbstractUnitOfWork,
        scope=Scope.REQUEST,
    )

    # Опциональнозакрытие engine при shutdown
    @provide(scope=Scope.APP, provides=AsyncEngine, is_singleton=True)
    async def get_engine_with_shutdown(self, engine: AsyncEngine):
        try:
            yield engine
        finally:
            await engine.dispose()
