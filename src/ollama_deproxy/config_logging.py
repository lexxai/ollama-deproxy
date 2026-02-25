import logging
from .config import settings

logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(level=settings.log_level)
    system_packages = ("python_multipart", "hpack", "httpcore", "httpx")
    for pkg in system_packages:
        logging.getLogger(pkg).setLevel(logging.WARNING)
