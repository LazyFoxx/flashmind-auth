import structlog
from uuid import UUID
from src.application.interfaces import AbstractRefreshTokenRepository


class LogoutUseCase:
    def __init__(
        self,
        refresh_token_repo: AbstractRefreshTokenRepository,
    ):
        self.refresh_token_repo = refresh_token_repo
        self.logger = structlog.get_logger(__name__)

    async def execute(self, user_id: UUID) -> None:
        await self.refresh_token_repo.revoke_by_user_id(user_id=user_id)
        self.logger.info("Произведен Logout пользователя", user_id=user_id)

        return None
