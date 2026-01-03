# src/application/interfaces/password_hasher.py
from abc import ABC, abstractmethod


class AbstractPasswordHasher(ABC):
    """Абстрактный интерфейс для хэширования и проверки паролей"""

    @abstractmethod
    def hash(self, password: str) -> str:
        """
        Хэширует открытый пароль и возвращает строку с хэшем

        Должен включать соль и параметры алгоритма

        Args:
            plain_password: Открытый пароль

        Returns:
            Строка с полным хэшем (например, $argon2id$v=19$m=65536,t=3,p=4$...)
        """
        ...

    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        """
        Проверяет, соответствует ли открытый пароль хэшу

        Args:
            plain_password: Открытый пароль
            hashed_password: Хэш из базы данных

        Returns:
            True, если пароль верный
        """
        ...
