import logging

from fastapi import FastAPI

from .api.routes import health_router, proxy_router
from .core.config import settings
from .core.lifespan import lifespan
from .core.logging import setup_logging
from .utils import common as utils

setup_logging()

logger = logging.getLogger(__name__)
opt = f"DEBUG_REQUEST={settings.debug_request},CACHE_ENABLED={settings.cache_enabled}"
if settings.force_model is not None:
    opt += f", force_model={settings.force_model} "
if settings.mirage_models is not None:
    opt += f", mirage_models={settings.mirage_models} "
logger.debug(f"Starting Ollama DeProxy with DEBUG logging... {opt}")

app = FastAPI(
    title="Ollama DeProxy",
    version=utils.app_version() or "0.0.1",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    redirect_slashes=False,
)

app.include_router(health_router)
app.include_router(proxy_router)
