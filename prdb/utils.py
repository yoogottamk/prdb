import asyncio
import contextlib
import os
import threading
import time

import uvicorn
from fastapi import WebSocket, WebSocketDisconnect


def is_fd_valid(fd: int) -> bool:
    """
    Check if fd provided is valid

    Args:
        fd: file descriptor
    """
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False


async def wait_till_readable(fd: int):
    """
    Wait till fd is ready to be read
    await-able alternative for `select.select`

    Args:
        fd: file descriptor
    """
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    loop.add_reader(fd, future.set_result, None)
    future.add_done_callback(lambda _f: loop.remove_reader(fd))
    await future


async def read_and_forward_output(ws: WebSocket, fd: int):
    """
    Waits till fd is ready to be read then reads and sends the output using ws

    Args:
        ws: websocket
        fd: file descriptor for pty
    """
    loop = asyncio.get_event_loop()

    while True:
        try:
            await asyncio.wait_for(wait_till_readable(fd), 10)

            if not is_fd_valid(fd):
                await ws.close()
                break
        except asyncio.TimeoutError:
            loop.remove_reader(fd)
            continue

        try:
            term_out = os.read(fd, 40960).decode()
            await ws.send_json({"output": term_out})
        except (WebSocketDisconnect, RuntimeError, OSError):
            break


class Server(uvicorn.Server):
    """
    Threaded uvicorn server with a context manager
    The server dies when context finishes

    taken from https://github.com/encode/uvicorn/issues/742#issuecomment-674411676
    """

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        """
        Start the server in thread and shutdown when context gets finished
        """
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()
