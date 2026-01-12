from src.application.interfaces import (
    AbstractHasher,
    AbstractUnitOfWork,
    AbstractAuthenticationService,
    AbstractRateLimitRepository,
)
from src.domain.value_objects import Email
from src.application.dtos import AuthCredentialsDTO, AuthResponseDTO
from src.core.settings import RateLimitConfig

from src.application.exceptions import (
    RateLimitExceededError,
)


class LoginCodeUseCase:
    def __init__(
        self,
        hasher: AbstractHasher,
        uow: AbstractUnitOfWork,
        authentication: AbstractAuthenticationService,
        rate_limit_repo: AbstractRateLimitRepository,
        rate_limit_cgf: RateLimitConfig,
    ):
        self.hasher = hasher
        self.uow = uow
        self.authentication = authentication
        self.login_limit = rate_limit_cgf.register_limit
        self.rate_limit_repo = rate_limit_repo
        self.login_window_seconds = rate_limit_cgf.register_window_seconds

    async def execute(self, input_dto: AuthCredentialsDTO) -> AuthResponseDTO:
        email_vo = Email.create(input_dto.email)
        # password_hash = HashedPassword(
        #     await asyncio.to_thread(self.hasher.hash, input_dto.password)
        # )

        # ищем пользователя в БД
        async with self.uow:
            user = await self.uow.users.get_by_email(email_vo.value)
            await self.uow.commit()

        if user is None:
            raise Exception

        # Rate limiting
        is_allowed, _, _ = await self.rate_limit_repo.increment_and_check(
            email=email_vo.value,
            prefix="login",
            limit_attempts=self.login_limit,
            window_seconds=self.login_window_seconds,
        )
        if not is_allowed:
            raise RateLimitExceededError(
                "Слишком много попыток регистрации, повторите попытку позже"
            )

        # генерируем токены доступа и сохраняем refresh в редис
        (
            access_token,
            refresh_token,
        ) = await self.authentication.authenticate_and_generate_tokens(user.id)

        return AuthResponseDTO(access_token, refresh_token)
