from __future__ import annotations
from email_validator import validate_email, EmailNotValidError
from dataclasses import dataclass
from src.domain.exceptions import InvalidEmailError


@dataclass(frozen=True, slots=True)
class Email:
    """
    Value Object для email-адреса.
    Гарантирует валидность и нормализацию при создании.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise InvalidEmailError("Email cannot be empty")

        normalized = self.value.strip().lower()
        if normalized != self.value:
            object.__setattr__(self, "value", normalized)

        try:
            validated = validate_email(normalized, check_deliverability=False)
            object.__setattr__(self, "value", validated.normalized)
        except EmailNotValidError as exc:
            raise InvalidEmailError(str(exc)) from exc

    @classmethod
    def create(cls, raw_email: str) -> "Email":
        """Фабричный метод — удобен для use cases"""
        return cls(raw_email)

    def __str__(self) -> str:
        return self.value
