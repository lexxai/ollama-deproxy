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


def filter_headers(headers):
    return {k: v for k, v in headers.items() if k.lower() not in excluded_headers}
