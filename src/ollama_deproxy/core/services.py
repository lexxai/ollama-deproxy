import asyncio

from ..services.network import HttpConnection, HttpConnectionManager
from .config import settings


def build_http_connection():
    return HttpConnection()


def build_http_connection_manager():
    return HttpConnectionManager()


def build_semaphore():
    return asyncio.Semaphore(
        settings.limit_concurrency
    )  # Stay safely under the 100 limit
