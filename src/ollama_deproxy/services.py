import httpx

from .config import settings


def build_session():
    headers = {}
    if settings.remote_auth_token:
        headers[settings.remote_auth_header] = settings.remote_auth_token.get_secret_value()

    headers["user-agent"] = f"Ollama-DeProxy/{settings.app_version};httpx/{httpx.__version__}"

    limits = httpx.Limits(
        max_connections=1000,  # Total allowed connections
        max_keepalive_connections=100,  # Allow more idle connections to stay open
        keepalive_expiry=5.0,
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
