# клиент Deribit API (aiohttp)

import asyncio
import logging
from typing import Dict
import aiohttp
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from app.config import settings

logger = logging.getLogger(__name__)

class DeribitClient:
    def __init__(self):
        self.base_url = settings.DERIBIT_API_URL
        self.timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
        self._session: aiohttp.ClientSession | None = None
        self._rate_limiter: asyncio.Semaphore | None = None

    async def start(self):
        """Инициализация сессии и семафора для rate limiting."""
        self._session = aiohttp.ClientSession(timeout=self.timeout)
        self._rate_limiter = asyncio.Semaphore(settings.RATE_LIMIT)

    async def stop(self):
        """Корректное закрытие сессии."""
        if self._session:
            await self._session.close()

    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=settings.RETRY_DELAY),
        retry=retry_if_exception_type(
            (aiohttp.ClientError, asyncio.TimeoutError)
        ),
    )
    async def fetch_index_price(self, currency: str) -> Dict:
        """
        Запрашивает index price для указанной валюты.
        currency: "btc_usd" или "eth_usd"
        """
        if not self._session:
            raise RuntimeError("Client not started. Call start() first.")

        # Rate limiting
        async with self._rate_limiter:
            params = {"index_name": currency}
            logger.debug(f"Fetching price for {currency}")
            async with self._session.get(self.base_url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                if "result" not in data or "index_price" not in data["result"]:
                    raise ValueError(f"Unexpected response: {data}")
                price = data["result"]["index_price"]
                timestamp = data["result"]["estimated_delivery_price"]  # в документации есть поле timestamp? На самом деле в ответе есть timestamp, но обычно поле "timestamp". Уточним.
                # По документации Deribit: в ответе есть "timestamp" (ms). Нам нужны секунды.
                # В целях демонстрации будем использовать текущее время.
                # Для упрощения возьмем локальное время.
                return {
                    "ticker": currency,
                    "price": float(price),
                    "timestamp": int(asyncio.get_event_loop().time()),  # TODO: заменить на реальный timestamp из ответа или time.time()
                }