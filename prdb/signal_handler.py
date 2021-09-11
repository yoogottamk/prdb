import code
import os
import pty
import signal
import sys
import types
from typing import Callable

from uvicorn import Config

from prdb.server import prdb_server
from prdb.utils import Server


def get_signal_handler(
    host: str = "127.0.0.1", port: int = 4242
) -> Callable[[int, types.FrameType], None]:
    """
    Returns the signal handler

    Args:
        host: on which host should the web server be started
        port: on which port should the web server be started
    """

    def prdb_signal_handler(_signum: int, frame: types.FrameType):
        """
        signal handler

        1. gets to the root execution frame
        2. forks the process
        3. starts an interactive console in the forked process with the
            variables from the root execution frame
        4. starts a web server and waits till child is alive
        """
        # go back to the root frame
        while frame.f_back is not None:
            frame = frame.f_back

        child_pid, child_fd = pty.fork()

        if child_pid == 0:
            # start a console in this forked process
            code.interact(banner="prdb", local=dict(frame.f_locals, **frame.f_globals))
            # once the user ends their console session, quit
            # we don't want to resume where we left off in the child
            sys.exit(0)

        # the child exits anyways
        # this will be executed only in parent
        print(f"http://{host}:{port}/console?fd={child_fd}")
        config = Config(
            prdb_server,
            host=host,
            port=port,
            log_level="info",
            loop="asyncio",
        )
        server = Server(config=config)

        with server.run_in_thread():
            # wait till the child is running
            os.wait()

        # once the child dies, the server is stopped
        # and the signal handler quits
        # resuming the old stuff the process was doing

    return prdb_signal_handler


def set_signal_handler(host: str = "127.0.0.1", port: int = 4242):
    """
    Set the signal handler

    Args:
        host: on which host should the web server be started
        port: on which port should the web server be started
    """
    signal.signal(signal.SIGUSR1, get_signal_handler(host, port))
