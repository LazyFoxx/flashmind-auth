class DomainError(Exception):
    """Базовый класс для доменных ошибок"""


class InvalidEmailError(DomainError):
    pass


class InvalidPasswordError(DomainError):
    pass


class UserAlreadyExistsError(DomainError):
    pass
