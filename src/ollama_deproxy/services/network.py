import logging
from asyncio import Lock
from dataclasses import dataclass

from httpx import AsyncClient, AsyncHTTPTransport, Limits, Timeout, __version__

from ..core.config import settings
from ..utils import common as utils

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class HttpConnectionOptions:
    base_url = str(settings.remote_url)
    retries: int = 10
    timeout: int = settings.remote_timeout
    http2: bool = settings.remote_url_http2
    follow_redirects: bool = True
    user_agent: str = f"Ollama-DeProxy/{utils.app_version};httpx/{__version__}"


class HttpConnection:
    """Manages the asynchronous HTTP connection to the Ollama server.

    Handles client initialization, connection limits, transport setup, and connection
    reconnection logic using asyncio locks for thread safety.
    """

    def __init__(self) -> None:
        """Initializes the HttpConnection with configured settings."""
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
            Timeout(self.options.timeout, connect=5.0)
            if self.options.timeout is not None
            else None
        )

    async def get_client(self) -> AsyncClient:
        """Retrieves the initialized or newly created AsyncClient.

        This method ensures that the client is only created once and is protected by a lock.

        Returns:
            AsyncClient: The active asynchronous HTTP client.
        """
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
        """Reestablishes the connection to the Ollama server.

        Logs the reconnection attempt and ensures the client is closed before attempting
        to create a new one.

        Returns:
            AsyncClient: The newly established asynchronous HTTP client.
        """
        logger.info("Reconnecting to Ollama server...")
        async with self._lock:
            await self._close_unlocked()
            return await self.get_client()

    async def _close_unlocked(self):
        """Closes the existing AsyncClient if it is open and sets the reference to None."""
        if self.client is not None:
            await self.client.aclose()
            self.client = None

    async def aclose(self):
        """Asynchronously closes the HTTP client connection."""
        async with self._lock:
            await self._close_unlocked()


# http_connection: HttpConnection = HttpConnection()
#
# __all__ = ["http_connection"]
