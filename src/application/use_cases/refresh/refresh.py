from src.application.dtos.auth_response_dto import AuthResponseDTO
from src.application.interfaces import (
    AbstractAuthenticationService,
)


class RefreshTokensUseCase:
    def __init__(
        self,
        authentication: AbstractAuthenticationService,
    ):
        self.authentication = authentication

    async def execute(self, refresh_token) -> AuthResponseDTO:
        # генерируем токены доступа и сохраняем refresh в редис
        (
            access_token,
            refresh_token,
        ) = await self.authentication.authenticate_and_generate_tokens(
            refresh_token=refresh_token
        )

        return AuthResponseDTO(access_token, refresh_token)
