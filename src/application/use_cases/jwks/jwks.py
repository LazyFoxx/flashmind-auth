from src.application.interfaces import AbstractJWTService


class JWKSUseCase:
    def __init__(
        self,
        jwt: AbstractJWTService,
    ):
        self.jwt = jwt

    async def execute(self) -> dict:
        return self.jwt.get_public_keys()
