from uuid import UUID
from typing import Tuple, Optional
from src.application.interfaces import (
    AbstractJWTService,
    AbstractRefreshTokenRepository,
    AbstractAuthenticationService,
)
from src.application.exceptions import InvalidTokenError, TokenReuseDetectedError


class AuthenticationService(AbstractAuthenticationService):
    """
    Конкретная реализация доменного сервиса аутентификации.
    Оркестрирует JWT-сервис и репозиторий refresh-токенов.
    Поддерживает single active session + rotation + reuse detection.
    """

    def __init__(
        self,
        jwt_service: AbstractJWTService,
        refresh_token_repo: AbstractRefreshTokenRepository,
    ):
        self.jwt_service = jwt_service
        self.refresh_token_repo = refresh_token_repo

    async def authenticate_and_generate_tokens(
        self,
        user_id: Optional[UUID] = None,
        refresh_token: Optional[str] = None,
        extra_claims: Optional[dict] = None,
    ) -> Tuple[str, str]:
        """
        Универсальный метод выдачи новой пары токенов.

        Если refresh_token передан:
            - Верифицируем его криптографически
            - Атомарно используем старый jti
            - Если consume не удался → reuse detection → revoke текущей сессии

        Всегда:
            - Генерируем новый access + новый refresh
            - Сохраняем новый jti (перезаписывает старый автоматически)
        """

        if user_id is None and refresh_token is None:
            raise ValueError("Either user_id or refresh_token must be provided")

        if refresh_token:
            try:
                payload = self.jwt_service.verify_refresh_token(refresh_token)
            except Exception as e:
                raise InvalidTokenError("Invalid or expired refresh token") from e

            old_jti = payload["jti"]

            user_id = UUID(payload["sub"])

            # Атомарный consume старого токена + reuse detection
            consumed_user_id = await self.refresh_token_repo.get_user_id_by_jti(old_jti)

            if consumed_user_id is None:
                # Reuse detected или токен уже отозван → сразу revoke текущую сессию  (logout)
                await self.refresh_token_repo.revoke_by_user_id(user_id)
                raise TokenReuseDetectedError(
                    "Refresh token reused or revoked – possible theft"
                )

        if user_id is None:
            raise ValueError()

        # Генерируем новую пару токенов
        access_token = self.jwt_service.create_access_token(
            user_id=user_id,
            extra_claims=extra_claims or {},
        )

        new_refresh_token = self.jwt_service.create_refresh_token(user_id=user_id)

        # Извлекаем jti нового refresh-токена
        new_payload = self.jwt_service.verify_refresh_token(new_refresh_token)
        new_jti = new_payload["jti"]

        # Сохраняем новый (автоматически перезаписывает старый → rotation)
        await self.refresh_token_repo.save(
            user_id=user_id,
            token_jti=new_jti,
        )

        return access_token, new_refresh_token
