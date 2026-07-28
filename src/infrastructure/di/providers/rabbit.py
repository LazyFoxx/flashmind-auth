from dishka import Provider, Scope, provide
from src.core.settings.rabbit import RabbitSettings
from src.infrastructure.rabbit import RabbitConnection, RabbitPublisher
from dishka.entities.key import DependencyKey
from typing import Callable

from src.application.interfaces import AbstractEventPublisher

USER_REGISTERED = DependencyKey(Callable, "user_registered")


class RabbitProvider(Provider):
    @provide(scope=Scope.APP)
    async def rabbit_connection(self, settings: RabbitSettings) -> RabbitConnection:
        conn = RabbitConnection(settings)
        await conn.connect()  # подключаемся один раз на всё приложение
        await conn.ensure_topology()  # настраиваем топологию
        return conn

    # @provide(scope=Scope.APP)
    # async def publisher(self, conn: RabbitConnection) -> RabbitPublisher:
    #     return RabbitPublisher(conn)
    
    @provide(scope=Scope.APP)
    async def event_publisher(self, conn: RabbitConnection) -> AbstractEventPublisher:
        """Возвращаем интерфейс, а не конкретную реализацию"""
        return RabbitPublisher(conn)
