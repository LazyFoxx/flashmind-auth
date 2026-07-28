from fastapi import APIRouter
from . import jwks as jwks_v1
from . import refresh as refresh_v1
from . import logout as logout_v1
from .email.router import api_router as email_router

api_router = APIRouter()


api_router.include_router(email_router)
api_router.include_router(refresh_v1.router)
api_router.include_router(logout_v1.router)
api_router.include_router(jwks_v1.router)
