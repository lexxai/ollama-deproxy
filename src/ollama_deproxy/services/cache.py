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
        return super().is_cached(path) and any(path.lower().startswith(cached) for cached in self.CACHED_PATHS)

    @staticmethod
    def add_mirage_models(response: Response, headers: dict):
        # replace models mode
        if settings.mirage_models_dict is not None:
            data = json.loads(response.body)
            models: list = data.get("models", [])
            mirage_dst: set[str] = set(settings.mirage_models_dict.values())
            for m in models:
                s_model = m.get("name")
                if s_model is None or (s_model not in mirage_dst):
                    continue
                for rs, rd in settings.mirage_models_dict.items():
                    if rd != s_model:
                        continue
                    dm = dict(m)
                    dm["name"] = rs
                    dm["model"] = rs
                    models.append(dm)
                    logger.debug(f"Added mirage model to model list: {dm['name']}")

            overlay_body = json.dumps(data).encode()
            headers["content-length"] = str(len(overlay_body))
            new_response = Response(
                content=overlay_body,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )
            response = new_response
            return response
        return None

    async def get_or_fetch(
        self,
        request: Request,
        path: str,
        http_connection,
        ollama_helper,
        body: bytes = None,
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
        response = await handler_root_response(path, request, http_connection, ollama_helper, decode_response=True)
        headers: dict[str, str] = dict(response.headers)  # noqa
        headers.pop("content-encoding", None)
        headers["content-length"] = str(len(response.body))
        # logger.debug(f"headers: {headers}")

        if (repaced_response := self.add_mirage_models(response, headers)) is not None:
            response = repaced_response

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
