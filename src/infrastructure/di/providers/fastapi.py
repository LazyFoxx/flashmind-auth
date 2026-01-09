# di/providers/fastapi.py
from dishka import Provider, Scope, provide, from_context
from fastapi import BackgroundTasks


class FastAPIProvider(Provider):
    background_tasks = provide(
        from_context(BackgroundTasks),  # берём из контекста запроса
        scope=Scope.REQUEST,
        provides=BackgroundTasks,
    )
