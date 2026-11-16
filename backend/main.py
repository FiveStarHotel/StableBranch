from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.api.v1.auth import router as router_auth
from backend.app.api.v1.health import router as router_health
from backend.app.api.v1.users import router as router_users
from backend.app.core.exceptions import AppError

ROUTER_PREFIX_V1 = "/api/v1"

app = FastAPI()

@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

app.include_router(router_health, prefix=ROUTER_PREFIX_V1, tags=["health check"])
app.include_router(router_auth, prefix=ROUTER_PREFIX_V1, tags=["authentication"])
app.include_router(router_users, prefix=ROUTER_PREFIX_V1, tags=["users"])
