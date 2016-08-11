"""
check issue #8
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__all__ = ['main']

import sys
import traceback
import signal
import time
import platform
import random
import pyownet
from pyownet import protocol
from . import (HOST, PORT)

A = 1e-3  # alarm interval
B = 1e-1  # max sleep in busy wait


def dummy_handler(signum, frame):
    """dummy signal handler"""


def main():

    print(platform.python_implementation(), platform.python_version())
    print(platform.system(), platform.release())
    print(pyownet.__name__, pyownet.__version__)

    owp = protocol.proxy(HOST, PORT, flags=protocol.FLG_UNCACHED)
    print(owp, 'vers.',
          protocol.bytes2str(owp.read(protocol.PTH_VERSION))
          if owp.present(protocol.PTH_VERSION) else 'unknown')

    signal.signal(signal.SIGALRM, dummy_handler)
    tic = time.time()
    signal.setitimer(signal.ITIMER_REAL, A, A)

    try:
        count = 0
        inter = 0
        while count < 10000:
            count += 1
            try:
                _ = owp.dir()
            except protocol.Error as exc:
                (_, val, tb) = sys.exc_info()
                assert val is exc
                inter += 1
                trs = traceback.extract_tb(tb)
                print(count, exc, trs[-1][0], trs[-1][1])
            time.sleep(random.uniform(0., B))  # can be interrupted
    except KeyboardInterrupt:
        print()
    signal.setitimer(signal.ITIMER_REAL, 0, A)
    elt = time.time() - tic
    print('{:d} errors / {:d} calls in {:.1f}s'.format(inter, count, elt))

if __name__ == '__main__':
    main()
