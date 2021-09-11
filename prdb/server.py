import asyncio
import os
from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from prdb.config import REPO_ROOT
from prdb.utils import is_fd_valid, read_and_forward_output

prdb_server = FastAPI(title="prdb", docs_url=None, redoc_url=None)

templates = Jinja2Templates(directory=str(REPO_ROOT / "templates"))


@prdb_server.get("/console", response_class=HTMLResponse)
def console(request: Request, fd: int):
    if not is_fd_valid(fd):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Invalid fd provided"
        )
    return templates.TemplateResponse("console.html", {"request": request, "fd": fd})


@prdb_server.websocket("/ws/connect")
async def connect(ws: WebSocket, fd: int):
    await ws.accept()
    asyncio.create_task(read_and_forward_output(ws, fd))

    while True:
        try:
            data = await ws.receive_json()
            os.write(fd, data.get("input", "").encode())
        except (WebSocketDisconnect, RuntimeError):
            break
