import os
import subprocess
import asyncio
import time
from typing import Optional

from pyngrok import ngrok


def start_ngrok(port: int = 8080, auth_token: Optional[str] = None, target: Optional[str] = None) -> str:
    """Start an ngrok tunnel to local `port` and return the public URL.

    If `auth_token` provided, set it before connecting.
    """
    if auth_token:
        ngrok.set_auth_token(auth_token)

    # If `target` is provided (like "caddy:80"), tunnel directly to that container/host:port
    addr = target if target else port
    tunnel = ngrok.connect(addr, "http")
    public_url = tunnel.public_url
    if not public_url.endswith("/"):
        public_url += "/"
    print("ngrok tunnel established:", public_url)
    return public_url


def start_uvicorn():
    # run uvicorn as subprocess
    cmd = ["uvicorn", "src.webapp:app", "--host", "0.0.0.0", "--port", "8000"]
    print("Starting uvicorn:", " ".join(cmd))
    return subprocess.Popen(cmd)


async def start_bot():
    # import bot module and run its main
    # this expects `src.bot` to expose `main()` coroutine
    from src import bot as bot_module
    await bot_module.main()


def main():
    auth = os.getenv("NGROK_AUTHTOKEN")
    # tunnel to Caddy inside compose network so public URL serves frontend via Caddy
    public = start_ngrok(port=8080, auth_token=auth, target="caddy:80")
    # export for other processes
    os.environ["WEBAPP_URL"] = public

    # start web server
    uv = start_uvicorn()
    # give uvicorn a moment
    time.sleep(1.5)

    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        try:
            uv.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    main()
