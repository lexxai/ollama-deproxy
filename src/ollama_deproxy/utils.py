import json
import logging

from .config import settings

excluded_headers = {
    "content-length",
    "connection",
    "server",
    "date",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "upgrade",
    "alt-svc",
}
if settings.decode_response:
    excluded_headers.add("content-encoding")

logger = logging.getLogger(__name__)


def filter_headers(headers, decode_response: bool = None):
    if decode_response is not None and settings.decode_response != decode_response and decode_response == True:
        excluded_headers_set = excluded_headers.copy()
        excluded_headers_set.add("content-encoding")
        return {k: v for k, v in headers.items() if k.lower() not in excluded_headers_set}
    else:
        return {k: v for k, v in headers.items() if k.lower() not in excluded_headers}


def debug_requests_data(body_bytes: bytes, method: str = "", target_url: str = ""):
    if settings.debug_request:
        if body_bytes:
            try:
                data = json.loads(body_bytes.decode())
            except json.JSONDecodeError:
                data = body_bytes.decode()
        else:
            data = ""
        logger.debug(f"Proxying request [{method.upper()}] to '{target_url}' with data: {data}")
