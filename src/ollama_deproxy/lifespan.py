import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .response_cache import ResponseCache
from .ollama_helper import OllamaHelper
from .services import build_session

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session = build_session()
    app.state.response_cache = ResponseCache()
    app.state.ollama_helper = OllamaHelper(app.state.session, app.state.response_cache)
    yield
    await app.state.session.aclose()
    app.state.response_cache.clear()
