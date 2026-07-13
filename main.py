from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import socket
import os
import time
import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

START_TIME = time.time()
request_count = 0


def get_container_id():
    # HOSTNAME is set by Docker to the container ID by default
    return os.environ.get("HOSTNAME", socket.gethostname())


def get_instance_name():
    # APP_NAME is set per-service in docker-compose.yml (app1/app2/app3).
    # Falls back to the raw container ID if it's ever missing.
    return os.environ.get("APP_NAME", get_container_id())


@app.get("/")
async def index(request: Request):
    global request_count
    request_count += 1
    uptime_seconds = int(time.time() - START_TIME)
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "instance_name": get_instance_name(),
        "container_id": get_container_id(),
        "request_count": request_count,
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
    },
)


@app.get("/health")
async def health():
    # Used by Nginx / uptime checks to confirm this instance is alive
    return JSONResponse({"status": "healthy", "instance": get_instance_name()})
