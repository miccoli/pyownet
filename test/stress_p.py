from __future__ import print_function

import atexit
import time
import threading

from pyownet import protocol
from . import (HOST, PORT)

MTHR = 10

tst = lambda: time.strftime('%T')


def log(s):
    print(tst(), s)


def main():
    proxy = protocol.proxy(HOST, PORT, verbose=False)
    pid = ver = ''
    try:
        pid = int(proxy.read('/system/process/pid'))
        ver = proxy.read('/system/configuration/version').decode()
    except protocol.OwnetError:
        pass
    log("{0}, pid={1:d}, {2}".format(proxy, pid, ver))

    delta = 1
    for i in range(MTHR):
        th = threading.Thread(target=worker, args=(proxy, i, ), )
        th.start()
        time.sleep(1.03*delta)
        delta *= 2


def worker(proxy, id):

    with protocol.clone(proxy, persistent=True) as pers:
        log('**[{0:02d}   ] {1}'.format(id, pers.conn))

        iter = 0
        nap = 1
        while True:
            time.sleep(nap)
            try:
                _ = pers.dir()
                log('..[{0:02d}.{1:02d}] {2}'.format(
                    id, iter, pers.conn))
            except protocol.Error as exc:
                log('!![{0:02d}] dead after {1:d}s: {2}'.format(id, nap, exc))
                break
            iter += 1
            nap *= 2


@atexit.register
def goodbye():
    log('exiting stress_p')

if __name__ == '__main__':
    main()
