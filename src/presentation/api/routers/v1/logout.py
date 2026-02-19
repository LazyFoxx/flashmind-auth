from fastapi import APIRouter, Depends, status, Response
from dishka.integrations.fastapi import FromDishka, inject
from src.presentation.api.dto.auth import MessageResponse
from src.secure.dependencies import get_current_user
from src.domain.entities.user import User

from src.application.use_cases import LogoutUseCase

router = APIRouter(tags=["logout"])


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse,
    summary="Выход с авторизации",
    description=(
        "Делает все токены не действительными, удаляет рефреш токен из cookie и завершает сессию."
    ),
)
@inject
async def logout(
    response: Response,
    use_case: FromDishka[LogoutUseCase],
    user: User = Depends(get_current_user),
) -> MessageResponse:
    await use_case.execute(user_id=user.id)

    response.delete_cookie(
        "refresh_token",
        #    domain="yourdomain.com",
        path="/",
    )

    return MessageResponse(message="Вы успешно вышли с авторизации")
