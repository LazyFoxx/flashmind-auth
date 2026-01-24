from passlib.context import CryptContext

from src.application.interfaces import AbstractHasher


class PasslibHasher(AbstractHasher):
    def __init__(self):
        # Настройки на 2025–2026 по OWASP
        # Цель: ~200–500 мс на верификацию на современном сервере
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto",  # если позже добавим другие схемы
            argon2__type="id",  # Argon2id — гибридный, самый рекомендуемый
            argon2__time_cost=4,  # итерации
            argon2__memory_cost=98304,
            argon2__parallelism=4,  # 4 потока
            argon2__hash_len=32,  # длина хэша
            argon2__salt_len=16,
        )

    def hash(self, plain_data: str) -> str:
        return self.pwd_context.hash(plain_data)

    def verify(self, plain_data: str, hashed_data: str) -> bool:
        return self.pwd_context.verify(plain_data, hashed_data)
