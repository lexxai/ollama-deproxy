import logging

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from .config import settings
from .utils import filter_headers

logger = logging.getLogger(__name__)


async def handler_root_response(path: str, request: Request, session):
    # logger.debug(f"Handling root request for path: {path}")
    target_url = f"{str(settings.remote_url).rstrip('/')}/{path.lstrip('/')}"

    proxy_headers = dict(request.headers)
    proxy_headers.pop("host", None)

    body = await request.body()

    async with session.stream(
        method=request.method,
        url=target_url,
        headers=proxy_headers,
        content=body,
        params=request.query_params,
        follow_redirects=False,
    ) as response:
        if settings.decode_response:
            await response.aread()
            response_content = response.content
        else:
            response_content = b"".join([chunk async for chunk in response.aiter_raw()])

    if response.status_code >= 400:
        logger.error(
            f"Error [{response.status_code}] on '{target_url}' with data: {body.decode()} : {response_content.decode()}"
        )

    return Response(
        content=response_content,
        status_code=response.status_code,
        headers=filter_headers(response.headers),
    )


async def handler_root_stream_response(path: str, request: Request, session):
    # logger.debug(f"Handling root stream request for path: {path}")

    target_url = f"{str(settings.remote_url).rstrip('/')}/{path.lstrip('/')}"

    headers = dict(request.headers)
    headers.pop("host", None)

    # async def request_body():
    #     async for chunk in request.stream():
    #         yield chunk

    body_bytes = await request.body()

    stream_ctx = session.stream(
        method=request.method,
        url=target_url,
        headers=headers,
        content=body_bytes,
        params=request.query_params,
        follow_redirects=False,
    )

    response = await stream_ctx.__aenter__()

    if response.status_code >= 400:  # Usually 400+ are the actual errors
        # 1. Fully consume the error body so we can see what happened
        error_content = await response.aread()

        # 2. Log it safely
        logger.error(
            f"Remote Error [{response.status_code}] on {target_url}. Body {body_bytes.decode()}: {error_content.decode(errors='ignore')}"
        )

        # 3. Clean up the stream context since we won't be streaming anymore
        await stream_ctx.__aexit__(None, None, None)

        # 4. Return a standard response instead of a StreamingResponse
        return Response(
            content=error_content, status_code=response.status_code, headers=filter_headers(response.headers)
        )

    # --- SUCCESS PATH ---
    response_aiter_method = response.aiter_bytes() if settings.decode_response else response.aiter_raw()

    return StreamingResponse(
        response_aiter_method,
        status_code=response.status_code,
        headers=filter_headers(response.headers),
        background=BackgroundTask(stream_ctx.__aexit__, None, None, None),
    )
