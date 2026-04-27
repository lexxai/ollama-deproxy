import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ollama_deproxy.core.services import build_http_connection, build_semaphore

from ..services.cache import ResponseCache
from ..services.ollama import OllamaHelper

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.response_cache = ResponseCache()
    app.state.http_connection = build_http_connection()
    client = await app.state.http_connection.get_client()
    app.state.ollama_helper = OllamaHelper(client, app.state.response_cache)
    app.state.semaphore = build_semaphore()
    yield
    await app.state.http_connection.aclose()
    app.state.response_cache.clear()
