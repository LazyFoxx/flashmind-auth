from abc import ABC, abstractmethod


class AbstractHasher(ABC):
    """Абстрактный интерфейс для хэширования и проверки паролей"""

    @abstractmethod
    def hash(self, plain_data: str) -> str:
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
    def verify(self, plain_data: str, hashed_data: str) -> bool:
        """
        Проверяет, соответствует ли открытые данные хэшу

        Args:
            plain_data: Открытый пароль / код верификации
            hashed_data: Хэш для сравнения

        Returns:
            True, если совпадает, иначе Fasle
        """
        ...
