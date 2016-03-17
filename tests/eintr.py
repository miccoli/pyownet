#
# check issue #8
#
import signal
import time
import platform
import pyownet
from pyownet import protocol
from . import (HOST, PORT)

count = 0


def dummy_handler(signum, frame):
    """dummy signal handler"""
    global count
    count += 1


def main():

    print(platform.python_implementation(), platform.python_version())
    print(platform.system(), platform.release())
    print(pyownet.__name__, pyownet.__version__)

    owp = protocol.proxy(HOST, PORT)
    ref = owp.dir()

    signal.signal(signal.SIGALRM, dummy_handler)
    tic = time.time()
    signal.setitimer(signal.ITIMER_REAL, 2, 0.01)

    try:
        while True:
            try:
                cur = owp.dir()
                assert cur == ref
            except protocol.Error as exc:
                print(count, exc)
            time.sleep(0.2)
    except KeyboardInterrupt:
        elt = time.time() - tic
        print('{:d} {:.1f}s {:.3f}s'.format(count, elt, elt/count))

if __name__ == '__main__':
    main()
