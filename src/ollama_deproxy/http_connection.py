import logging
from asyncio import Lock

from httpx import AsyncClient, __version__, Limits, Timeout, AsyncHTTPTransport

from ollama_deproxy.config import settings

from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class HttpConnectionOptions:
    base_url = str(settings.remote_url)
    retries: int = 10
    timeout: int = settings.remote_timeout
    http2: bool = settings.remote_url_http2
    follow_redirects: bool = True
    user_agent: str = f"Ollama-DeProxy/{settings.app_version};httpx/{__version__}"


class HttpConnection:
    def __init__(self) -> None:
        self.client: AsyncClient | None = None
        self._lock = Lock()
        self.options = HttpConnectionOptions()
        self.headers = {"user-agent": self.options.user_agent}
        if settings.remote_auth_token:
            self.headers[settings.remote_auth_header] = (
                settings.remote_auth_token.get_secret_value()
            )
        self.limits = Limits(
            max_connections=1000,  # Total allowed connections
            max_keepalive_connections=100,  # Allow more idle connections to stay open
            keepalive_expiry=5.0,
        )
        self.transport = AsyncHTTPTransport(retries=self.options.retries)
        self.timeout = (
            Timeout(self.options.timeout) if self.options.timeout is not None else None
        )

    async def get_client(self) -> AsyncClient:
        async with self._lock:
            if self.client is None:
                self.client = AsyncClient(
                    base_url=self.options.base_url,
                    http2=self.options.http2,
                    headers=self.headers,
                    follow_redirects=self.options.follow_redirects,
                    limits=self.limits,
                    timeout=self.timeout,
                    transport=self.transport,
                )
            return self.client

    async def re_connect(self) -> AsyncClient:
        logger.info("Reconnecting to Ollama server...")
        async with self._lock:
            await self._close_unlocked()
            return await self.get_client()

    async def _close_unlocked(self):
        if self.client is not None:
            await self.client.aclose()
            self._client = None

    async def aclose(self):
        async with self._lock:
            await self._close_unlocked()


# http_connection: HttpConnection = HttpConnection()
#
# __all__ = ["http_connection"]
