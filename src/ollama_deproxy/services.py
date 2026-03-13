import asyncio


from .config import settings
from .http_connection import HttpConnection


def build_http_connection():
    return HttpConnection()


def build_semaphore():
    return asyncio.Semaphore(
        settings.limit_concurrency
    )  # Stay safely under the 100 limit
