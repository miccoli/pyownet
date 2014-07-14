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


def main():
    proxy = protocol.OwnetProxy(HOST, PORT, verbose=False)
    pid = ver = ''
    try:
        pid = int(proxy.read('/system/process/pid'))
        ver = proxy.read('/system/configuration/version').decode()
    except protocol.OwnetError:
        pass
    print "{0}, pid={1:d}, {2}".format(proxy, pid, ver)

    delta = 1
    for i in range(MTHR):
        th = threading.Thread(target=worker, args=(proxy, i, ), )
        th.start()
        time.sleep(1.03*delta)
        delta *= 2


def worker(proxy, id):

    with proxy.persistent_clone() as pers:
        print '**[{0:02d}] {1}'.format(id, pers.conn)

        nap = 1
        while True:
            nap *= 2
            time.sleep(nap)
            try:
                pers.dir()
            except protocol.Error as exc:
                print '!![{0:02d}] dead after {1:d}s: {2}'.format(id, nap, exc)
                break

if __name__ == '__main__':
    main()
