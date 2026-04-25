import hashlib
from os import environ
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, SecretStr, field_validator

from .utils import app_version

BASE_PATH = Path(__file__).parent.parent
load_dotenv(BASE_PATH.parent / ".env")


class Settings(BaseModel):
    """Application settings for the Ollama DeProxy service.

    Configuration parameters are loaded from environment variables.
    """

    model_config = ConfigDict(validate_default=True)

    remote_url: HttpUrl = Field(
        default=environ.get("REMOTE_URL"), description="Proxy server URL"
    )
    path_proxy_ollama: str = Field(default=environ.get("PATH_PROXY_OLLAMA", "ollama/"))
    path_api: str = Field(default=environ.get("PATH_API", "api/"))
    remote_url_http2: bool = Field(default=environ.get("REMOTE_URL_HTTP2", True))
    remote_auth_header: str = Field(
        default=environ.get("REMOTE_AUTH_HEADER", "Authorization")
    )
    remote_auth_token: SecretStr | None = Field(
        default=environ.get("REMOTE_AUTH_TOKEN")
    )
    remote_timeout: int | None = Field(default=environ.get("REMOTE_TIMEOUT", None))
    remote_total_timeout: int | None = Field(
        default=environ.get("REMOTE_TOTAL_TIMEOUT", 60 * 10)
    )  # 10 minutes
    local_port: int = Field(default=environ.get("LOCAL_PORT", "11434"))
    log_level: str = Field(default=environ.get("LOG_LEVEL", "INFO"))
    app_version: str | None = Field(default=None)
    stream_response: bool = Field(default=environ.get("STREAM_RESPONSE", True))
    decode_response: bool = Field(default=environ.get("DECODE_RESPONSE", False))
    debug_request: bool = Field(default=environ.get("DEBUG_REQUEST", False))
    debug_request_model_only: bool = Field(
        default=environ.get("DEBUG_REQUEST_MODEL_ONLY", False)
    )
    correct_numbered_model_names: bool = Field(
        default=environ.get("CORRECT_NUMBERED_MODEL_NAMES", False)
    )

    cache_enabled: bool = Field(default=environ.get("CACHE_ENABLED", True))
    cache_maxsize: int = Field(default=environ.get("CACHE_MAXSIZE", 512))  # 512 entries
    cache_ttl: int = Field(default=environ.get("CACHE_TTL", 60 * 60 * 12))  # 12 hours
    hash_algorithm: str = Field(
        default=environ.get("HASH_ALGORITHM", "auto"),
        description="Hash algorithm to use for caching. Set to 'auto' to use the default algorithm.",
    )
    force_model: str | None = Field(
        default=environ.get("FORCE_MODEL", None),
        description="Relace used model in query request.",
    )
    mirage_model: str | None = Field(
        default=environ.get("MIRAGE_MODEL", None),
        description="add to list of models mirage model in query request.",
    )

    limit_concurrency: int = Field(default=environ.get("LIMIT_CONCURRENCY", 90))

    @field_validator("hash_algorithm", mode="after")
    @classmethod
    def normalize_hash_algorithm(cls, v):
        if isinstance(v, str):
            v = v.lower()
            if v == "auto":
                return v
            if v not in hashlib.algorithms_available:
                raise ValueError(
                    f"Hash algorithm '{v}' is not supported. List of available algorithms: {','.join(hashlib.algorithms_available)}"
                )
        return v

    @field_validator("remote_auth_token", mode="after")
    @classmethod
    def validate_remote_auth_token(cls, v):
        if not v:
            print(
                "WARNING: No remote auth token provided. Proxy will not be authenticated."
            )
        return v

    @field_validator("app_version", mode="before")
    @classmethod
    def fill_version(cls, v):
        if not v:
            v = app_version()
        return v
