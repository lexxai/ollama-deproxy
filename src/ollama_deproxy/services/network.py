import logging
from asyncio import Lock
from dataclasses import dataclass
from enum import StrEnum, auto

from httpx import AsyncClient, AsyncHTTPTransport, Limits, Timeout, __version__

from ..core.config import settings
from ..utils import common as utils

logger = logging.getLogger(__name__)


class ClientID(StrEnum):
    OLLAMA = auto()
    OLLAMA_CLOUD = auto()


@dataclass(frozen=True, slots=True)
class HttpConnectionOptions:
    base_url: str = str(settings.remote_url)
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

    client: AsyncClient | None = None
    headers = {}

    def __init__(
        self,
        options: HttpConnectionOptions | None = None,
        auth_header: dict | None = None,
    ) -> None:
        """Initializes the HttpConnection with configured settings."""

        self._lock = Lock()
        self.options = options or HttpConnectionOptions()
        self.headers = {"user-agent": self.options.user_agent}
        self.set_auth_header(auth_header)
        self.limits = Limits(
            max_connections=1000,  # Total allowed connections
            max_keepalive_connections=100,  # Allow more idle connections to stay open
            keepalive_expiry=5.0,
        )
        self.transport = AsyncHTTPTransport(retries=self.options.retries)
        self.timeout = Timeout(self.options.timeout, connect=5.0) if self.options.timeout is not None else None

    def set_auth_header(self, auth_header: dict = None):
        if auth_header is not None:
            self.headers = self.headers | auth_header
            return

        if settings.remote_auth_token:
            self.headers[settings.remote_auth_header] = settings.remote_auth_token.get_secret_value()

    async def get_client(self) -> AsyncClient | None:
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
                print()
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


class HttpConnectionManager:
    connections: dict[str, HttpConnection | None] | None = None

    def __init__(self) -> None:
        self.connections = {}
        client_id = ClientID.OLLAMA_CLOUD
        if settings.ollama_cloud_url and settings.ollama_api_key:
            options = HttpConnectionOptions(base_url=str(settings.ollama_cloud_url))
            self.connections[client_id] = HttpConnection(options, self.get_auth_header(client_id))

        client_id = ClientID.OLLAMA
        options = HttpConnectionOptions()
        self.connections[client_id] = HttpConnection(options, self.get_auth_header(client_id))

    async def get_client(self, client_id: ClientID = ClientID.OLLAMA) -> AsyncClient | None:
        if self.connections is None:
            logger.error(f"Connection for {client_id} isn't initialized yet.")
            return None
        connection = self.connections.get(client_id)
        return await connection.get_client() if connection is not None else None

    async def aclose(self):
        if self.connections is None:
            return
        for v in self.connections.values():
            if v is not None:
                await v.aclose()

    async def re_connect(self):
        if self.connections is None:
            return
        for v in self.connections.values():
            if v is not None:
                await v.re_connect()

    @staticmethod
    def get_auth_header(client_id: ClientID = ClientID.OLLAMA) -> dict:
        headers = {}
        match client_id:
            case ClientID.OLLAMA_CLOUD:
                if settings.ollama_api_key:
                    headers["Authorization"] = "Bearer " + settings.ollama_api_key.get_secret_value()
            case ClientID.OLLAMA:
                if settings.remote_auth_token:
                    headers[settings.remote_auth_header] = settings.remote_auth_token.get_secret_value()
        return headers


# http_connection: HttpConnection = HttpConnection()
#
# __all__ = ["http_connection"]
