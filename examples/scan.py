"""scan.py -- scan the owserver given on the command line

scan.py [server[:port]] ...

print some info on the sensors on owserver at 'server:port'
default is 'localhost:4304'

"""
from __future__ import print_function

import sys

from pyownet import protocol


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
            proxy = protocol.proxy(host, port)
        except (protocol.ConnError, protocol.ProtocolError) as err:
            print(err)
            continue
        pid = None
        ver = None
        try:
            pid = int(proxy.read('/system/process/pid'))
            ver = proxy.read('/system/configuration/version').decode()
        except protocol.OwnetError:
            pass
        print('{0}, pid = {1:d}, ver = {2}'.format(proxy, pid, ver))
        print('{0:^17} {1:^7} {2:>7}'.format('id', 'type', 'temp.'))
        for sensor in proxy.dir(slash=False, bus=False):
            stype = proxy.read(sensor + '/type').decode()
            try:
                temp = float(proxy.read(sensor + '/temperature'))
                temp = "{0:.2f}".format(temp)
            except protocol.OwnetError:
                temp = ''
            print('{0:<17} {1:<7} {2:>7}'.format(sensor, stype, temp))

if __name__ == '__main__':
    main()
