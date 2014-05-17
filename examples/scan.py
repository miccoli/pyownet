from __future__ import print_function

import sys

from pyownet.protocol import (OwnetProxy, ConnError, ProtocolError, OwnetError)

def main():
    if len(sys.argv) >= 2:
        args = sys.argv[1:]
    else:
        args = ['localhost']
    for netloc in args:
        print('{0:=^33}'.format(netloc))
        try:
            host, port = netloc.split(':', 1)
        except ValueError:
            host, port = netloc, 4304
        try:
            proxy = OwnetProxy(host, port)
        except (ConnError, ProtocolError) as err:
            print(err)
            continue
        pid = None
        ver = None
        try:
            pid = int(proxy.read('/system/process/pid'))
            ver = proxy.read('/system/configuration/version')
        except OwnetError:
            pass
        print('{0}, pid = {1:d}, ver = {2}'.format(proxy, pid, ver))
        print('{0:^17} {1:^7} {2:>7}'.format('id', 'type', 'temp.'))
        for sensor in proxy.dir(slash=False, bus=False):
            stype = proxy.read(sensor + '/type').decode('ascii')
            try:
                temp = float(proxy.read(sensor + '/temperature'))
                temp = "{0:.2f}".format(temp)
            except OwnetError:
                temp = ''
            print('{0:<17} {1:<7} {2:>7}'.format(sensor, stype, temp))

if __name__ == '__main__':
    main()
