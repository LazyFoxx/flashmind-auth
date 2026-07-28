import jwt
import structlog
from authlib.jose import JoseError
from authlib.jose.errors import ExpiredTokenError, InvalidClaimError

from src.application.exceptions import InvalidTokenError
from src.core.settings.telegram import TelegramSettings

from .jwks_client import TelegramJWKSClient
from src.application.use_cases import TelegramLoginInput


class TelegramTokenService:
    def __init__(self, settings: TelegramSettings, jwks: TelegramJWKSClient):
        self.settings = settings
        self.jwks = jwks
        self.logger = structlog.get_logger(__name__)

    async def execute(self, token: str) -> TelegramLoginInput:
        try:
            # 1. Получаем заголовок токена без проверки подписи
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            # 2. Получаем ключ по kid
            key = await self.jwks.get_key(kid)
            
            if key is None:
                self.logger.warning(f"Ключ не найден для kid: {kid}")
                raise InvalidTokenError("Подходящий телеграм ключ не найден")
             
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256", "ES256"],
                audience=self.settings.client_id,
                issuer="https://oauth.telegram.org",
                options={"require": ["iss", "aud", "exp", "iat", "sub"]},
                leeway=30,
            )
            
            # 4. Извлекаем данные пользователя
            tg_user_id = payload.get("sub")
            name = payload.get("name")
            username = payload.get("preferred_username")
            avatar_url = payload.get("picture")
            phone = payload.get("phone_number")

            # 5. Возвращаем результат
            return TelegramLoginInput(
                tg_user_id=tg_user_id,
                name=name,
                username=username,
                avatar_url=avatar_url,
                phone=phone,
            )

        except (ExpiredTokenError, InvalidClaimError, JoseError, ValueError) as e:
            self.logger.warning(f"Ошибка валидации токена: {e}")
            raise InvalidTokenError(str(e)) from e
