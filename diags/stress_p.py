"""this diagnostic program stresses persistent connections.

At 60 s. intervals a new thread is started that holds an open persistent
connection to the owserver.

Each persistent connection is queried at increasing intervals of time.
"""

from __future__ import print_function

from pyownet import protocol

import atexit
try:
    from time import monotonic
except ImportError:
    # pretend that time.time is monotonic
    from time import time as monotonic
from time import strftime, sleep
import threading
import sys
if sys.version_info < (3, ):
    from urlparse import (urlsplit, )
else:
    from urllib.parse import (urlsplit, )


def log(s):
    print(strftime('%T'), s)


def main():
    assert len(sys.argv) == 2
    urlc = urlsplit(sys.argv[1], scheme='owserver', allow_fragments=False)
    host = urlc.hostname or 'localhost'
    port = urlc.port or 4304
    assert not urlc.path or urlc.path == '/'

    proxy = protocol.proxy(host, port, verbose=False)
    pid = -1
    ver = ''
    try:
        pid = int(proxy.read('/system/process/pid'))
        ver = proxy.read('/system/configuration/version').decode()
    except protocol.OwnetError:
        pass
    log("{0}, pid={1:d}, {2}".format(proxy, pid, ver))

    delta = 60
    assert threading.active_count() is 1
    started = 0
    while threading.active_count() == started + 1:
        th = threading.Thread(target=worker, args=(proxy, started, ), )
        th.start()
        started += 1
        try:
            sleep(delta)
        except KeyboardInterrupt:
            break
    log('started {0:d} worker threads'.format(started))
    log('still waiting for {0:d} worker threads'
        .format(threading.active_count()-1))


def worker(proxy, wid):

    with protocol.clone(proxy, persistent=True) as pers:
        try:
            pers.ping()
        except protocol.Error as exc:
            log('xx[{0:02d}   ] {1}'.format(wid, exc))
            return

        tlast = monotonic()
        conn = pers.conn
        log('**[{0:02d}   ] {1}'.format(wid, pers.conn))

        gen = 0
        nap = 1
        while True:
            sleep(nap)
            try:
                pers.dir()
                tlast = monotonic()
                log('..[{0:02d}.{1:02d}]'.format(wid, gen))
                if pers.conn is not conn:
                    log('..[{0:02d}.{1:02d}] {2}'.format(
                        wid, gen, pers.conn))
                    conn = pers.conn
            except protocol.Error as exc:
                log('!![{0:02d}.{1:02d}] dead after {2:.1f}s: {3}'.format(
                    wid, gen, monotonic() - tlast, exc))
                break
            gen += 1
            nap *= 2


@atexit.register
def goodbye():
    log('exiting stress_p')

if __name__ == '__main__':
    main()
