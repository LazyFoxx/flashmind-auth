class ApplicationError(Exception):
    """Базовый класс для application ошибок"""


class EmailAlreadyExistsError(ApplicationError):
    """Email уже занят"""

    def __init__(self, email: str):
        super().__init__(f"Email уже используется: {email}")
        self.email = email


class UserNotFoundError(ApplicationError):
    """Пользователь с таким Email не найден"""

    def __init__(self, email: str):
        super().__init__(f"Пользователь с таким email не найден: {email}")
        self.email = email


class InvalidCredentialsError(ApplicationError):
    "неверные данные ( чаще всего логин или пароль при login)"


class CooldownEmailError(ApplicationError):
    """Кулдаун имейла еще не истек"""

    def __init__(self, remaining_seconds: int):
        super().__init__(f"Отправьте код позже: {remaining_seconds} секунды")
        self.remaining_seconds = remaining_seconds


class CodeAttemptError(ApplicationError):
    """Неверный код"""

    def __init__(self, remaining_attempts: int):
        super().__init__(f"Неверный код, осталось попыток: {remaining_attempts}")
        self.remaining_attempts = remaining_attempts


class RateLimitExceededError(ApplicationError):
    """Слишком частые попытки регистрации"""


class LimitCodeAttemptsError(ApplicationError):
    """Закончились попытки ввода кода"""

    pass


class RequestExpiredError(ApplicationError):
    """ключ не найден - начать регистрацию заново при регистрации или при сбросе пароля"""

    pass


class InvalidTokenError(ApplicationError):
    """токен недействителен/истёк"""

    pass


class TokenReuseDetectedError(ApplicationError):
    """Вызывается когда обнаружена анамалия вызваранная возможной
    попыткой переиспользовать истекший токен"""

    pass
