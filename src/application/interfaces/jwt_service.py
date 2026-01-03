# src/application/interfaces/jwt_service.py
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Dict, Any, Optional
from uuid import UUID


class AbstractJWTService(ABC):
    """Абстрактный сервис для работы с JWT-токенами"""

    @abstractmethod
    def create_access_token(
        self,
        user_id: UUID,
        extra_claims: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Создаёт access-токен (короткоживущий)

        Args:
            user_id: ID пользователя
            extra_claims: дополнительные claims (roles, permissions и т.д.)
            expires_delta: кастомное время жизни
        """
        ...

    @abstractmethod
    def create_refresh_token(
        self,
        user_id: UUID,
        token_jti: Optional[str] = None,  # уникальный ID токена для ротации
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Создаёт refresh-токен (долгоживущий, с jti)
        """
        ...

    @abstractmethod
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """
        Верифицирует и декодирует access-токен

        Returns:
            payload (claims)

        Raises:
            InvalidTokenError: если токен недействителен/истёк
        """
        ...

    @abstractmethod
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Верифицирует refresh-токен (дополнительные проверки jti и т.д.)
        """
        ...

    @abstractmethod
    def get_public_keys(self) -> Dict[str, Any]:
        """
        Возвращает JWKS (JSON Web Key Set) для валидации другими сервисами
        """
        ...
