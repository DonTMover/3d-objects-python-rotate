from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from os import path
from fastapi import Body
from fastapi.responses import JSONResponse
import time
from collections import deque

HEARTBEATS = deque()  # store timestamps (float)
BOT_START = None


app = FastAPI()

# serve templates and (optional) static dir
HERE = path.dirname(__file__)
templates_dir = path.join(HERE, "templates")
static_dir = path.join(HERE, "static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/status")
async def status():
    """Return current webapp URL and basic info for debugging.

    The `serve_and_ngrok.py` script sets `WEBAPP_URL` in the environment
    before starting the web server; this endpoint exposes it for container logs.
    """
    from os import getenv
    return {
        "webapp_url": getenv("WEBAPP_URL", ""),
        "have_pyrender": True if getenv("HAVE_PYRENDER") == "1" else False,
    }


@app.post("/heartbeat")
async def heartbeat(payload: dict = Body(...)):
    """Receive heartbeat pings from bot. Payload may contain 'ts' and 'bot_start'."""
    try:
        ts = float(payload.get("ts", time.time()))
    except Exception:
        ts = time.time()
    HEARTBEATS.append(ts)
    # keep last 48 hours max (safety)
    cutoff = time.time() - 48 * 3600
    while HEARTBEATS and HEARTBEATS[0] < cutoff:
        HEARTBEATS.popleft()
    global BOT_START
    if payload.get("bot_start"):
        BOT_START = payload.get("bot_start")
    return JSONResponse({"status": "ok"})


@app.get("/metrics")
async def metrics(minutes: int = 60):
    """Return aggregated heartbeats per minute for the last `minutes` minutes."""
    now = time.time()
    window_start = now - minutes * 60
    # build buckets per minute
    buckets = [0] * minutes
    for ts in HEARTBEATS:
        if ts < window_start:
            continue
        idx = int((ts - window_start) // 60)
        if 0 <= idx < minutes:
            buckets[idx] += 1
    # build labels (minute offsets)
    labels = []
    for i in range(minutes):
        t = window_start + i * 60
        labels.append(int(t))
    return {"labels": labels, "counts": buckets, "bot_start": BOT_START}


@app.get("/stats", response_class=HTMLResponse)
async def stats(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request})
