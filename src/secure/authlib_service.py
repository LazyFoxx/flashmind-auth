from datetime import timedelta, datetime, timezone
from typing import Dict, Any, Optional
from uuid import UUID

from authlib.jose import JsonWebKey, JoseError, JsonWebToken
from authlib.jose.errors import ExpiredTokenError, InvalidClaimError
from src.application.exceptions import InvalidTokenError

from src.application.interfaces.jwt_service import AbstractJWTService
from src.core.settings.jwt import JwtSettings
from uuid import uuid4


class AuthlibJWTService(AbstractJWTService):
    """
    JWT-сервис на основе authlib с поддержкой RS256 и JWKS
    Готов к расширению
    """

    def __init__(self, settings: JwtSettings):
        self.settings = settings

        # Загружаем ключи
        with open(settings.private_key_path) as f:
            self.private_key = JsonWebKey.import_key(f.read(), {"kty": "RSA"})
        with open(settings.public_key_path) as f:
            self.public_key = JsonWebKey.import_key(f.read(), {"kty": "RSA"})

        self.alg = "RS256"
        self.kid = settings.key_id
        self.issuer = settings.issuer

        self.jwt = JsonWebToken([self.alg])

        # JWKS для публичного доступа
        self.jwks = {
            "keys": [
                self.public_key.as_dict(
                    private=False, kid=self.kid, use="sig", alg=self.alg
                )
            ]
        }

    def _prepare_headers(self) -> dict:
        return {
            "typ": "JWT",
            "alg": self.alg,
            "kid": self.kid,
        }

    def create_access_token(
        self,
        user_id: UUID,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        expires_in = timedelta(minutes=self.settings.access_expire_minutes)
        claims = {
            "sub": str(user_id),
            "iss": self.issuer,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + expires_in,
            **(extra_claims or {}),
        }

        return self.jwt.encode(self._prepare_headers(), claims, self.private_key)

    def create_refresh_token(
        self,
        user_id: UUID,
    ) -> str:
        expires_in = timedelta(days=self.settings.refresh_expire_days)
        claims = {
            "sub": str(user_id),
            "type": "refresh",
            "jti": str(uuid4()),
            "iss": self.issuer,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + expires_in,
        }

        return self.jwt.encode(self._prepare_headers(), claims, self.private_key)

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        try:
            claims = self.jwt.decode(
                token,
                self.public_key,
                claims_options={
                    "iss": {"essential": True, "value": self.issuer},
                    "sub": {"essential": True},
                    "exp": {"essential": True},
                    "iat": {"essential": True},
                    # "nbf": {"essential": False},
                    # "aud": {"essential": True, "value": "..."}
                    # "scope": {"essential": False},
                },
            )
            return claims
        except ExpiredTokenError:
            raise InvalidTokenError("Token expired")
        except InvalidClaimError as e:
            raise InvalidTokenError(f"Invalid claim: {e}")
        except JoseError as e:
            raise InvalidTokenError(f"Invalid token: {e}")

    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        try:
            claims = self.jwt.decode(
                token,
                self.public_key,
                claims_options={
                    "iss": {"essential": True, "value": self.issuer},
                    "sub": {"essential": True},
                    "exp": {"essential": True},
                    "iat": {"essential": True},
                    "type": {"essential": True, "value": "refresh"},
                },
            )
            return claims

        except ExpiredTokenError:
            raise InvalidTokenError("Refresh token has expired")
        except InvalidClaimError as e:
            raise InvalidTokenError(f"Invalid refresh token claim: {e}")
        except JoseError as e:
            raise InvalidTokenError(f"Invalid refresh token: {e}")

    def get_public_keys(self) -> Dict[str, Any]:
        return self.jwks
