from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    return JSONResponse({"status": "ok"})
