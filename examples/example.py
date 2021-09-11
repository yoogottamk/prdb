import os
import signal
from time import sleep

# just importing it is enough
# it sets the signal handler and is ready...
import prdb


class Foo:
    """
    a class
    """

    def __init__(self):
        self.bar = 0


def send_signal():
    """
    This is emulating a `kill -USR1 PID` call from outside
    """
    os.kill(os.getpid(), signal.SIGUSR1)


if __name__ == "__main__":
    var = Foo()

    # ...but you can change some parameters of the handler as well
    prdb.set_signal_handler(host="0.0.0.0", port=8080)

    for i in range(1000):
        sleep(1)
        print(i)
        if i == 1:
            # update the object on heap
            var.bar += 1
        elif i == 2:
            # send the signal that triggers web console start
            send_signal()
