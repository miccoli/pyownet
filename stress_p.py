from __future__ import print_function
import time
import threading
from ConfigParser import ConfigParser

from pyownet import protocol


config = ConfigParser()

config.add_section('server')
config.set('server', 'host', 'localhost')
config.set('server', 'port', '4304')

config.read(['tests.ini'])

HOST = config.get('server', 'host')
PORT = config.get('server', 'port')

MTHR = 6

tst = lambda: time.strftime('%T')
def log(s):
    print(tst(), s)

def main():
    proxy = protocol.OwnetProxy(HOST, PORT, verbose=False)
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

    with proxy.clone_persistent() as pers:
        log('**[{0:02d}] {1}'.format(id, pers.conn))

        iter = 0
        nap = 1
        while True:
            time.sleep(nap)
            try:
                res = pers.dir()
                log('..[{0:02d}.{2:d}] {1}'.format(id, res, iter))
            except protocol.Error as exc:
                log('!![{0:02d}] dead after {1:d}s: {2}'.format(id, nap, exc))
                break
            iter += 1
            nap *= 2

if __name__ == '__main__':
    main()
