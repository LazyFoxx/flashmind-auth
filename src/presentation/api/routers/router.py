from fastapi import APIRouter
from .v1 import jwks as jwks_v1
from .v1 import refresh as refresh_v1
from .v1 import reset_password as reset_password_v1
from .v1 import register as register_v1
from .v1 import login as login_v1
from .v1 import logout as logout_v1

api_router = APIRouter()

api_router.include_router(register_v1.router, prefix="/api/v1/auth")
api_router.include_router(login_v1.router, prefix="/api/v1/auth")
api_router.include_router(reset_password_v1.router, prefix="/api/v1/auth")
api_router.include_router(refresh_v1.router, prefix="/api/v1/auth")
api_router.include_router(logout_v1.router)
api_router.include_router(jwks_v1.router)
