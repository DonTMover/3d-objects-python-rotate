from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from os import path

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
