import httpx

from .config import settings


def build_session():
    headers = {}
    if settings.remote_auth_token:
        headers[settings.remote_auth_header] = settings.remote_auth_token.get_secret_value()

    limits = httpx.Limits(
        max_keepalive_connections=50,
        max_connections=100,
    )
    timeout = httpx.Timeout(settings.remote_timeout) if settings.remote_timeout is not None else None

    return httpx.AsyncClient(
        base_url=str(settings.remote_url),
        http2=settings.remote_url_http2,
        headers=headers,
        follow_redirects=False,
        limits=limits,
        timeout=timeout,
    )
