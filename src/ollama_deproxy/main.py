import logging

from fastapi import FastAPI, Depends
from starlette.requests import Request

from .config import settings
from .config_logging import setup_logging
from .depends import get_session
from .handlers import handler_root_response, handler_root_stream_response
from .lifespan import lifespan

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ollama DeProxy",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    redirect_slashes=False,
)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def root(path: str, request: Request, session=Depends(get_session)):
    if settings.stream_response:
        return await handler_root_stream_response(path, request, session)
    else:
        return await handler_root_response(path, request, session)


def run():
    import uvicorn

    port = settings.local_port or 11434
    uvicorn.run("ollama_deproxy.main:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    run()
