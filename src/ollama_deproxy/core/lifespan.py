import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..core.services import (
    build_http_connection_manager,
    build_semaphore,
)
from ..services.cache import ResponseCache
from ..services.network import ClientID
from ..services.ollama import OllamaHelper

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.response_cache = ResponseCache()
    app.state.http_connection = build_http_connection_manager()
    client_ollama = await app.state.http_connection.get_client(ClientID.OLLAMA)
    app.state.ollama_helper = OllamaHelper(client_ollama, app.state.response_cache)
    app.state.semaphore = build_semaphore()
    yield
    await app.state.http_connection.aclose()
    app.state.response_cache.clear()
