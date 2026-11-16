from fastapi import FastAPI

from backend.app.api.v1.health import router as router_health

app = FastAPI()

app.include_router(router_health)