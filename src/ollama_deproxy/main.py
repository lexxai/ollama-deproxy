import asyncio
import logging

from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import Response

from . import utils
from .config import settings
from .config_logging import setup_logging
from .depends import (
    get_http_connection,
    get_ollama_helper,
    get_response_cache,
    get_semaphore,
)
from .handlers import handler_root_response, handler_root_stream_response
from .lifespan import lifespan

setup_logging()

logger = logging.getLogger(__name__)
opt = f"DEBUG_REQUEST={settings.debug_request},CACHE_ENABLED={settings.cache_enabled}"
if settings.force_model is not None:
    opt += f", forced by model={settings.force_model} "
logger.debug(f"Starting Ollama DeProxy with DEBUG logging... {opt}")

app = FastAPI(
    title="Ollama DeProxy",
    version=utils.app_version() or "0.0.1",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    redirect_slashes=False,
)

ollama_compatible_prefixes = {"api", "v1"}
anthropic_compatibility_prefixes = ("v1/messages",)


def gen_path(path: str):
    """
    Determines the correct path prefix for proxying based on Ollama or Anthropic compatibility.

    Args:
        path: The incoming request path.

    Returns:
        A tuple containing the modified path string and the path split by the first slash.
    """
    path_split = path.split("/", maxsplit=1)[0]
    if path_split == "":
        return path, path_split

    for prefix in anthropic_compatibility_prefixes:
        if path.startswith(prefix):
            path = settings.path_api + path
            logger.debug(
                f"Proxying request corrected to '{path}' for Anthropic compatibility"
            )
            return path, path_split

    if path_split in ollama_compatible_prefixes:
        path = settings.path_proxy_ollama + path
        return path, path_split

    path = settings.path_proxy_ollama + "v1/" + path
    logger.debug(f"Proxying request corrected to '{path}' for OpenAI compatibility")

    return path, path_split


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
)
async def root(
    path: str,
    request: Request,
    http_connection=Depends(get_http_connection),
    ollama_helper=Depends(get_ollama_helper),
    response_cache=Depends(get_response_cache),
    semaphore=Depends(get_semaphore),
):
    """
    Handles all incoming API requests by routing them through the path generation,
    caching, and actual response handling logic.

    Args:
        path: The requested API path.
        request: The incoming Starlette Request object.
        http_connection: Dependency for HTTP connection management.
        ollama_helper: Dependency for Ollama interaction helper.
        response_cache: Dependency for response caching.
        semaphore: Dependency for concurrency limiting.

    Returns:
        The final HTTP Response object.
    """
    path, path_split = gen_path(path)
    if path_split == "":
        return Response("Ollama is running")

    client = await http_connection.get_client()

    cached_response = await response_cache.get_or_fetch(
        request, path, client, ollama_helper
    )
    if cached_response is not None:
        return cached_response

    async with semaphore:
        try:
            logger.debug(f"*** Handling request for path: /{path}")
            if settings.stream_response:
                response = await asyncio.wait_for(
                    handler_root_stream_response(path, request, client, ollama_helper),
                    timeout=settings.remote_total_timeout,
                )
                return response
                # return await handler_root_stream_response(
                #     path, request, client, ollama_helper
                # )
            else:
                response = await asyncio.wait_for(
                    handler_root_response(path, request, client, ollama_helper),
                    timeout=settings.remote_total_timeout,
                )
                return response
                # return await handler_root_response(path, request, client, ollama_helper)
        except asyncio.TimeoutError:
            logger.error(
                f"The request took longer than {settings.remote_total_timeout} seconds total!"
            )
        except Exception as e:
            logger.error(f"root: {e} {type(e)}, try reconnection")
            await http_connection.re_connect()
            raise
