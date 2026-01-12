class ApplicationError(Exception):
    """Базовый класс для application ошибок"""


class EmailAlreadyExistsError(ApplicationError):
    """Email уже занят"""

    def __init__(self, email: str):
        super().__init__(f"Email уже используется: {email}")
        self.email = email  # удобно для обработчика / логирования


class RateLimitExceededError(ApplicationError):
    """Слишком частые попытки регистрации"""


class LimitCodeAttemptsError(ApplicationError):
    """Закончились попытки ввода кода"""

    pass


class CodeAttemptError(ApplicationError):
    """Неверный код"""

    pass


class RequestExpiredError(ApplicationError):
    """ключ не найден - начать регистрацию заново"""

    pass


class CooldownEmailError(ApplicationError):
    """Кулдаун имейла еще не истек"""

    pass


class InvalidTokenError(ApplicationError):
    """токен недействителен/истёк"""

    pass


class TokenReuseDetectedError(ApplicationError):
    """Вызывается когда обнаружена анамалия вызваранная возможной
    попыткой переиспользовать истекший токен"""

    pass
