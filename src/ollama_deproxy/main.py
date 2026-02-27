import logging
from http.client import HTTPResponse

from fastapi import FastAPI, Depends
from starlette.requests import Request
from starlette.responses import Response

from .config import settings
from .config_logging import setup_logging
from .depends import get_session, get_ollama_helper
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

ollama_compatible_prefixes = {"api", "v1"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def root(path: str, request: Request, session=Depends(get_session), ollama_helper=Depends(get_ollama_helper)):
    path_split = path.split("/", maxsplit=1)[0]
    if path_split == "":
        return Response("Ollama is running")

    if not (path_split == "" or path_split in ollama_compatible_prefixes):
        path = "v1/" + path
        logger.debug(f"Proxying request corrected to '{path}' for OpenAI compatibility")
    if settings.stream_response:
        return await handler_root_stream_response(path, request, session, ollama_helper)
    else:
        return await handler_root_response(path, request, session, ollama_helper)


def run():
    import uvicorn

    port = settings.local_port or 11434
    uvicorn.run("ollama_deproxy.main:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    run()
