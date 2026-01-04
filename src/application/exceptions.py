from exceptions import Exception


class ApplicationError(Exception):
    """Базовый класс для application ошибок"""


class EmailAlreadyExistsError(ApplicationError):
    pass


class RateLimitExceededError(ApplicationError):
    pass
