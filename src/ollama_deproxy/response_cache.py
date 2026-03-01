import logging

from starlette.requests import Request
from starlette.responses import Response

from .cache_base import CacheBase
from .handlers import handler_root_response

logger = logging.getLogger(__name__)


class ResponseCache(CacheBase):

    CACHED_PATHS = ("api/tags", "api/models", "api/show")

    def is_cached(self, path: str) -> bool:
        """Check if the given path should be cached."""
        return any(path.lower().startswith(cached) for cached in self.CACHED_PATHS)

    async def get_or_fetch(
        self, request: Request, path: str, session, ollama_helper, body: bytes = None
    ) -> Response | None:
        """Get a cached response or fetch and cache a new one."""
        if not self.is_cached(path):
            return None

        if request is None:
            logger.error(f"request is None for path: {path}")
            return None

        body = body or await request.body()

        cache_key = await self.async_build_cache_key(path, request.method, body)

        # Try to get from the cache
        cached = await self.get_cache(path, cache_key=cache_key)
        if cached is not None:
            return Response(
                content=cached.get("content"),
                status_code=cached.get("status_code", 200),
                headers=cached.get("headers", {}),
            )

        # Fetch not streaming response if not cached
        response = await handler_root_response(path, request, session, ollama_helper, decode_response=True)
        headers = dict(response.headers)
        # headers.pop("content-encoding", None)
        # headers["content-length"] = str(len(response.body))
        # logger.debug(f"headers: {headers}")

        # Cache the response if valid
        if isinstance(response, Response):
            await self.set_cache(
                path, cache_key=cache_key, content=response.body, status_code=response.status_code, headers=headers
            )

        return response
