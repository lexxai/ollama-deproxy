import logging
import time

from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from .config import settings
from .ollama_helper import OllamaHelper
from .utils import filter_headers, debug_requests_data

logger = logging.getLogger(__name__)


def build_proxy_headers(request: Request):
    proxy_headers = dict(request.headers)
    proxy_headers.pop("host", None)
    proxy_headers.pop("authorization", None)
    return proxy_headers


def get_duration_str(start_time: float):
    duration = time.perf_counter() - start_time
    minutes = int(duration // 60)
    seconds = duration - (minutes * 60)
    duration_str = f"{minutes:02d}:{seconds:04.1f}"
    return duration_str


async def handler_root_response(
    path: str, request: Request, client, ollama_helper: OllamaHelper, decode_response: bool = None
):
    # logger.debug(f"Handling root request for path: {path}")
    target_url = f"{str(settings.remote_url).rstrip('/')}/{path.lstrip('/')}"

    method = request.method
    query_params = request.query_params
    decode_response = decode_response or settings.decode_response

    proxy_headers = build_proxy_headers(request)

    body_bytes = await request.body() if request else b""

    debug_requests_data(body_bytes, method, target_url)

    if settings.correct_numbered_model_names and not path.startswith(ollama_helper.MODEL_PATH):
        body_bytes = await ollama_helper.replace_numbered_model(body_bytes)
        proxy_headers["content-length"] = str(len(body_bytes))
    start_time = time.perf_counter()
    try:
        async with client.stream(
            method=method,
            url=target_url,
            headers=proxy_headers,
            content=body_bytes,
            params=query_params,
            follow_redirects=False,
        ) as response:
            if decode_response:
                await response.aread()
                response_content = response.content
                # logger.debug(f"Response session.headers: {session.headers}")
            else:
                response_content = b"".join([chunk async for chunk in response.aiter_raw()])
    except Exception as e:
        logger.error(f"handler_root_response: {e}")
        if str(e).startswith("Max outbound streams"):
            raise
        return Response(
            content="Error remote side",
            status_code=500,
        )
    finally:
        duration_str = get_duration_str(start_time)
        logger.debug(f"*** Finished response for /{path} in {duration_str}")

    if response.status_code >= 400:
        logger.error(
            f"Error [{response.status_code}] on '{target_url}' with data: {body_bytes.decode()} : {response_content.decode()}"
        )

    return Response(
        content=response_content,
        status_code=response.status_code,
        headers=filter_headers(response.headers, decode_response=decode_response),
    )


async def handler_root_stream_response(path: str, request: Request, client, ollama_helper: OllamaHelper):
    # logger.debug(f"Handling root stream request for path: {path}")

    target_url = f"{str(settings.remote_url).rstrip('/')}/{path.lstrip('/')}"

    method = request.method
    query_params = request.query_params

    proxy_headers = build_proxy_headers(request)

    # async def request_body():
    #     async for chunk in request.stream():
    #         yield chunk
    start_time = time.perf_counter()
    try:
        body_bytes = await request.body() if request else b""

        debug_requests_data(body_bytes, method, target_url)

        if settings.correct_numbered_model_names:
            body_bytes = await ollama_helper.replace_numbered_model(body_bytes)
            proxy_headers["content-length"] = str(len(body_bytes))

        stream_ctx = client.stream(
            method=method,
            url=target_url,
            headers=proxy_headers,
            content=body_bytes,
            params=query_params,
            follow_redirects=False,
        )
        response = await stream_ctx.__aenter__()
    except Exception as e:
        logger.error(f"handler_root_stream_response: {e}")
        if str(e).startswith("Max outbound streams"):
            raise
        return Response(
            content="Error remote side",
            status_code=500,
        )

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

    async def cleanup_and_log():
        await stream_ctx.__aexit__(None, None, None)
        duration_str = get_duration_str(start_time)
        logger.debug(f"*** Finished up stream for /{path} in {duration_str}")

    return StreamingResponse(
        response_aiter_method,
        status_code=response.status_code,
        headers=filter_headers(response.headers),
        background=BackgroundTask(cleanup_and_log),
    )
