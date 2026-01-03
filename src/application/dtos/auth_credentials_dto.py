from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthCredentialsDTO:
    email: str
    password: str
