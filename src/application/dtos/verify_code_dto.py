from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VerifyCodeDTO:
    email: str
    code: str
