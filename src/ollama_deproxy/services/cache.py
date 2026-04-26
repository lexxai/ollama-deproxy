import json
import logging

from starlette.requests import Request
from starlette.responses import Response

from ..api.handlers import handler_root_response
from ..core.config import settings
from ..utils.cache_base import CacheBase

logger = logging.getLogger(__name__)


class ResponseCache(CacheBase):
    CACHED_PATHS = (
        settings.path_proxy_ollama + "api/tags",
        settings.path_proxy_ollama + "api/models",
        settings.path_proxy_ollama + "api/show",
    )

    def is_cached(self, path: str) -> bool:
        return super().is_cached(path) and any(
            path.lower().startswith(cached) for cached in self.CACHED_PATHS
        )

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
        response = await handler_root_response(
            path, request, session, ollama_helper, decode_response=True
        )
        headers: dict[str, str] = dict(response.headers)
        headers.pop("content-encoding", None)

        # replace models mode
        if (
            settings.force_model is not None
            and (mirage_models := settings.mirage_models) is not None
        ):
            data = json.loads(response.body)
            models: list = data.get("models", [])
            for m in models:
                f_model = m.get("name")
                if not f_model or (f_model != settings.force_model):
                    continue
                for mirage in mirage_models:
                    dm = dict(m)
                    dm["name"] = mirage
                    dm["model"] = mirage
                    models.append(dm)
                    logger.debug(f"Added mirage model to model list: {mirage}")

                overlay_body = json.dumps(data).encode()
                headers["content-length"] = str(len(overlay_body))
                new_response = Response(
                    content=overlay_body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=response.media_type,
                )
                response = new_response
                break

        headers["content-length"] = str(len(response.body))
        # logger.debug(f"headers: {headers}")

        # Cache the response if valid
        if isinstance(response, Response):
            await self.set_cache(
                path,
                cache_key=cache_key,
                content=response.body,
                status_code=response.status_code,
                headers=headers,
            )

        return response
