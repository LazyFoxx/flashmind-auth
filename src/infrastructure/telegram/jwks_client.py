from typing import Optional

import httpx
from authlib.jose import JsonWebKey

from src.application.interfaces import AbstractJWKSCache
from src.core.settings import TelegramSettings


class TelegramJWKSClient:
    def __init__(self, cache: AbstractJWKSCache, settings: TelegramSettings):
        self.url = settings.jwks_url
        self.ttl = 3600
        self.cache = cache
        self._memory: dict[str, JsonWebKey] = {}

    async def get_key(self, kid: str) -> Optional[JsonWebKey]:
        # L1 cache
        if kid in self._memory:
            return self._memory[kid]

        # L2 cache
        key = await self.cache.get(kid)
        if key:
            self._memory[kid] = key
            return key

        # JWKS endpoint
        async with httpx.AsyncClient() as client:
            jwks = (await client.get(self.url)).json()

        for k in jwks["keys"]:
            try:
                parsed = JsonWebKey.import_key(k)
                self._memory[k["kid"]] = parsed
                await self.cache.set(k["kid"], parsed, self.ttl)
            except (ValueError, KeyError):
                # Пропускаем неподдерживаемые алгоритмы (EdDSA и т.д.)
                continue
            
        return self._memory.get(kid)
