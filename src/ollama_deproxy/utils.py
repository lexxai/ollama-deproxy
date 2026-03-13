import json
import logging

from . import __version__

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


logger = logging.getLogger(__name__)


def filter_headers(headers, decode_response: bool = None):
    from .config import settings

    if (
        decode_response is not None
        and settings.decode_response != decode_response
        and decode_response
    ):
        excluded_headers_set = excluded_headers.copy()
        excluded_headers_set.add("content-encoding")
        return {
            k: v for k, v in headers.items() if k.lower() not in excluded_headers_set
        }
    else:
        excluded_headers_set = excluded_headers.copy()
        if settings.decode_response:
            excluded_headers_set.add("content-encoding")
        return {
            k: v for k, v in headers.items() if k.lower() not in excluded_headers_set
        }


def debug_requests_data(body_bytes: bytes, method: str = "", target_url: str = ""):
    from .config import settings

    if settings.debug_request:
        if body_bytes:
            try:
                data = json.loads(body_bytes.decode())
            except json.JSONDecodeError:
                data = body_bytes.decode()
        else:
            data = ""
        logger.debug(
            f"Proxying request [{method.upper()}] to '{target_url}' with data: {data}"
        )


def decode_error(e):
    from .settings_base import Settings

    for error in e.errors():
        field_name = ".".join(str(loc) for loc in error["loc"])
        error_msg = error["msg"]

        # Get field description from Pydantic model
        field_info = (
            Settings.model_fields.get(error["loc"][0]) if error["loc"] else None
        )
        field_description = (
            field_info.description
            if field_info and hasattr(field_info, "description")
            else "No description available"
        )

        print(f"Error for field: '{field_name}'")
        print(f"  Description: {field_description}")
        print(f"  Error: {error_msg}")

    print(
        "\nError: Invalid environment variables. Please check your .env file or redefine them using command-line arguments. Run `ollama-deproxy --help` for more information."
    )


def print_header():
    import os
    import sys

    from .get_version import app_version

    """Print decorative header with icons to console."""
    print("\n" + "=" * 60)
    print(f"🚀 Ollama DeProxy Server v{app_version()}")
    print("=" * 60)
    if sys.platform == "win32":
        os.system(f"title Ollama DeProxy Server 🚀 [{__version__}]")
    print()
