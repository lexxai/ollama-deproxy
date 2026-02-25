from os import environ
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, HttpUrl, Field, field_validator, SecretStr, ConfigDict

BASE_PATH = Path(__file__).parent.parent

load_dotenv(BASE_PATH.parent / ".env")


class Settings(BaseModel):
    model_config = ConfigDict(validate_default=True)

    remote_url: HttpUrl = Field(default=environ.get("REMOTE_URL"))
    remote_url_http2: bool = Field(default=environ.get("REMOTE_URL_HTTP2", True))
    remote_auth_header: str = Field(default=environ.get("REMOTE_AUTH_HEADER", "Authorization"))
    remote_auth_token: SecretStr | None = Field(default=environ.get("REMOTE_AUTH_TOKEN"))
    remote_timeout: int | None = Field(default=environ.get("REMOTE_TIMEOUT", None))
    local_port: int = Field(default=environ.get("LOCAL_PORT", "11434"))
    log_level: str = Field(default=environ.get("LOG_LEVEL", "INFO"))
    app_version: str | None = Field(default=None)
    stream_response: bool = Field(default=environ.get("STREAM_RESPONSE", True))
    decode_response: bool = Field(default=environ.get("DECODE_RESPONSE", False))

    @field_validator("app_version", mode="before")
    @classmethod
    def fill_version(cls, v):
        if not v:
            v = "0.0.1"
            try:
                pyproject_file = BASE_PATH.parent / "pyproject.toml"
                if pyproject_file.exists():
                    import tomllib

                    with pyproject_file.open("rb") as f:
                        v = tomllib.load(f)["project"]["version"]
            except Exception as e:
                print(f"Error app_version: {e}")
        return v


settings = Settings()

# from pprint import pprint

# pprint(settings.model_dump())
