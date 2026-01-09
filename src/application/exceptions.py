class ApplicationError(Exception):
    """Базовый класс для application ошибок"""


class EmailAlreadyExistsError(ApplicationError):
    """Пользователь с таким email уже существует"""

    pass


class RateLimitExceededError(ApplicationError):
    pass


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
