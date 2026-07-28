from fastapi import APIRouter
from . import reset_password as reset_password_v1
from . import register as register_v1
from . import login as login_v1

api_router = APIRouter(tags=["email"], prefix="/email")

api_router.include_router(register_v1.router)
api_router.include_router(login_v1.router)
api_router.include_router(reset_password_v1.router)
