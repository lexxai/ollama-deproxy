import asyncio

from ..services.network import HttpConnection
from .config import settings


def build_http_connection():
    return HttpConnection()


def build_semaphore():
    return asyncio.Semaphore(
        settings.limit_concurrency
    )  # Stay safely under the 100 limit
