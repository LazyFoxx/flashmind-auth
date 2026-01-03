# src/domain/value_objects/hashed_password.py
from __future__ import annotations
from dataclasses import dataclass
from domain.exceptions import InvalidPasswordError


@dataclass(frozen=True, slots=True)
class HashedPassword:
    """
    Value Object для хэшированного пароля.
    Не позволяет создавать из произвольной строки — только из результата PasswordHasher.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.startswith("$"):
            raise InvalidPasswordError("Hashed password must be a valid hash string")

    @classmethod
    def from_hasher(cls, hashed_str: str) -> "HashedPassword":
        """Единственный разрешённый способ создания"""
        return cls(hashed_str)

    def __str__(self) -> str:
        return self.value
