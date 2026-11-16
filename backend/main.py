from fastapi import FastAPI

from backend.app.api.v1.health import router as router_health

ROUTER_PREFIX_V1 = "/api/v1"

app = FastAPI()

app.include_router(router_health, prefix=ROUTER_PREFIX_V1, tags=["health check"])