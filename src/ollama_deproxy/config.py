from pathlib import Path

from dotenv import load_dotenv

from .settings_base import Settings

BASE_PATH = Path(__file__).parent.parent
load_dotenv(BASE_PATH.parent / ".env")

settings = Settings()
