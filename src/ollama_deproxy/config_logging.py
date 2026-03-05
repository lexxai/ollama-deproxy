import logging

from .config import settings

logger = logging.getLogger(__name__)


def setup_logging():
    import uvicorn

    stream_handler = logging.StreamHandler()
    formatter = uvicorn.logging.DefaultFormatter(  # type: ignore
        "%(asctime)s %(levelprefix)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", use_colors=True
    )
    stream_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(stream_handler)
    logger.setLevel(settings.log_level)

    system_packages = ("python_multipart", "hpack", "httpcore", "httpx")
    for pkg in system_packages:
        logging.getLogger(pkg).setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").name = "system"
