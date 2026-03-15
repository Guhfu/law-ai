from datetime import date

from fastapi import FastAPI

from .config import get_settings
from .routers import search as search_router
from .schemas import HealthResponse


settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", time=date.today())


app.include_router(search_router.router)

