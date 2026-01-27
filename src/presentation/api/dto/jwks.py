from pydantic import BaseModel
from typing import List


class JWK(BaseModel):
    kty: str  # RSA / OKP
    kid: str  # key id
    use: str  # sig
    alg: str  # RS256 / EdDSA
    n: str | None = None  # RSA modulus
    e: str | None = None  # RSA exponent


class JWKSResponse(BaseModel):
    keys: List[JWK]
