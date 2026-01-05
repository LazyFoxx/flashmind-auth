# src/application/interfaces/password_hasher.py
from abc import ABC, abstractmethod


class AbstractHasher(ABC):
    """Абстрактный интерфейс для хэширования и проверки паролей"""

    @abstractmethod
    def hash(self, password: str) -> str:
        """
        Хэширует открытый пароль/код и возвращает строку с хэшем

        Должен включать соль и параметры алгоритма

        Args:
            plain_data: Открытый пароль / код верификации

        Returns:
            Строка с полным хэшем (например, $argon2id$v=19$m=65536,t=3,p=4$...)
        """
        ...

    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        """
        Проверяет, соответствует ли открытый текст хэшу

        Args:
            plain_data: Открытый пароль
            hashed_data: Хэш из базы данных

        Returns:
            True, если совпадает, иначе Fasle
        """
        ...
