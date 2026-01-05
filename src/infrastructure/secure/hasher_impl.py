from passlib.hash import argon2  # или bcrypt


class PasswordHasher:
    def hash(self, plaintext: str) -> str:
        return argon2.hash(plaintext)  # автоматически генерирует соль

    def verify(self, plaintext: str, hashed: str) -> bool:
        return argon2.verify(plaintext, hashed)  # constant-time, безопасно
