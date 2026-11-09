from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/health")
def check_health():
    return HTMLResponse("I'm alive!", status_code=status.HTTP_200_OK)
