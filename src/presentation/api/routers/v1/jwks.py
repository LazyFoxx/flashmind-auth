from fastapi import APIRouter, Response, status
from dishka.integrations.fastapi import FromDishka, inject
from src.presentation.api.dto.jwks import JWK, JWKSResponse


from src.application.use_cases import (
    JWKSUseCase,
)

router = APIRouter()


@router.get(
    "/.well-known/jwks.json",
    response_model=JWKSResponse,
    status_code=status.HTTP_200_OK,
    summary="Эндпоинт для получения публичных ключей (JWKS)",
    description="Выдает JWKS (JSON Web Key Set) для валидации JWT",
    tags=["well-known"],
)
@inject
async def get_jwks(
    use_case: FromDishka[JWKSUseCase], response: Response
) -> JWKSResponse:
    jwks = await use_case.execute()
    print(jwks)

    response.headers["Cache-Control"] = "public, max-age=3600"

    return JWKSResponse(keys=[JWK(**key) for key in jwks["keys"]])
