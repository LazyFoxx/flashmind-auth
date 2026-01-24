from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from authlib.jose import JsonWebKey, JsonWebToken, JoseError
from authlib.jose.errors import ExpiredTokenError, InvalidClaimError
from src.core.settings.jwt import JwtSettings
from src.application.interfaces.unit_of_work import AbstractUnitOfWork
from src.application.exceptions import InvalidTokenError

from src.domain.entities.user import User


bearer_scheme = HTTPBearer()


@inject
async def get_current_user(
    settings: FromDishka[JwtSettings],
    uow: FromDishka[AbstractUnitOfWork],
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    token = credentials.credentials
    jwt = JsonWebToken(["RS256"])
    issuer = settings.issuer

    with open(settings.public_key_path) as f:
        public_key = JsonWebKey.import_key(f.read(), {"kty": "RSA"})

    try:
        claims = jwt.decode(
            token,
            public_key,
            claims_options={
                "iss": {"essential": True, "value": issuer},
                "sub": {"essential": True},
                "exp": {"essential": True},
                "iat": {"essential": True},
                # "nbf": {"essential": False},
                # "aud": {"essential": True, "value": "..."}
                # "scope": {"essential": False},
            },
        )
    except ExpiredTokenError:
        raise InvalidTokenError("Token expired")
    except InvalidClaimError:
        raise InvalidTokenError("Invalid claim")
    except JoseError:
        raise InvalidTokenError("Invalid token")

    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject (sub)",
        )

    async with uow:
        user = await uow.users.get_by_id(user_id)
        await uow.commit()

    return user
