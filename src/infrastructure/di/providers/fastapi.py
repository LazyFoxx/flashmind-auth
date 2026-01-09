from dishka import Provider, Scope, from_context
from fastapi import BackgroundTasks


class FastAPIProvider(Provider):
    background_tasks = from_context(BackgroundTasks, scope=Scope.REQUEST)
