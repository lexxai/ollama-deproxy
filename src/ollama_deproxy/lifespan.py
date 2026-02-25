import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .services import build_session

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session = build_session()
    yield
    await app.state.session.aclose()
