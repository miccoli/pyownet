from __future__ import print_function
import sys
import platform
import timeit
import argparse
if sys.version_info < (3, ):
    from urlparse import (urlsplit, urlunsplit)
else:
    from urllib.parse import (urlsplit, urlunsplit)

import pyownet
from pyownet import protocol


def main():

    def report(name, res):
        scale = 1e3  # report times in ms
        print('  * {:17}'.format(name), end=':')
        for t in (sorted(res)):
            print(' {:6.3f} ms'.format(t / number * scale), end=',')
        print()

    parser = argparse.ArgumentParser()
    parser.add_argument('uri', metavar='URI', nargs='?', default='/',
                        help='[owserver:]//server:port/entity')
    parser.add_argument('-n', '--number', type=int, default=20,
                        metavar='N',
                        help='number of executions (default: %(default)s)')
    parser.add_argument('-r', '--repeat', type=int, default=5,
                        metavar='R',
                        help='repeat count (default: %(default)s)')

    args = parser.parse_args()
    urlc = urlsplit(args.uri, scheme='owserver', allow_fragments=False)
    if urlc.scheme != 'owserver':
        parser.error("Invalid URI scheme '{}:'".format(urlc.scheme))
    assert not urlc.fragment
    if urlc.query:
        parser.error(
            "Invalid URI '{}', no query component allowed".format(args.uri))
    host = urlc.hostname or 'localhost'
    port = urlc.port or 4304
    path = urlc.path or '/'

    try:
        base = protocol.proxy(host, port, persistent=False)
    except protocol.ConnError as exc:
        sys.exit('Error connecting to {}:{} {}'.format(host, port, exc))
    pid = 'unknown'
    ver = 'unknown'
    try:
        pid = int(base.read(protocol.PTH_PID))
        ver = base.read(protocol.PTH_VERSION).decode()
    except protocol.OwnetError:
        pass

    number = args.number
    repeat = args.repeat

    print('python  : {} {} on {}'.format(platform.python_implementation(),
                                         platform.python_version(),
                                         platform.platform(terse=True),))
    print('{:8s}: {}'.format(pyownet.__name__, pyownet.__version__))
    print('owproxy : {}'.format(base))
    print('owserver: pid {}, ver. {}'.format(pid, ver))
    print('url     : {}'.format(urlunsplit(urlc), ))
    print('samples : {} * {} repetitions'.format(number, repeat))
    print()

    global data, owproxy, hargs
    data = (b'\x00\x00\x00\x00\x00\x000:\xff\xff\xff\xfe\x00\x00\x00\x00\x00'
            b'\x00\x04\xd2\x00\x00\x00\xea')
    hargs = {'payload': 745, 'type': protocol.MSG_READ,
             'flags': protocol.FLG_UNCACHED | protocol.FLG_TEMP_C,
             'size': 234, 'offset': 52}

    print('{} core objects'.format(pyownet.__name__))

    setup = """
from pyownet.protocol import _FromServerHeader, _ToServerHeader, proxy
from __main__ import data, hargs
"""
    stmt = "_FromServerHeader(data)"

    timer = timeit.Timer(stmt=stmt, setup=setup)
    res = timer.repeat(number=number, repeat=repeat)
    report('_FromServerHeader', res)

    stmt = "_ToServerHeader(**hargs)"

    timer = timeit.Timer(stmt=stmt, setup=setup)
    res = timer.repeat(number=number, repeat=repeat)
    report('_ToServerHeader', res)

    stmt = "proxy(host='{}', port={})".format(host, port)

    timer = timeit.Timer(stmt=stmt, setup=setup)
    res = timer.repeat(number=number, repeat=repeat)
    report('proxy()', res)

    setup = "from __main__ import owproxy"
    stmt = "owproxy.ping()"

    print(stmt)

    owproxy = protocol.clone(base, persistent=False)
    timer = timeit.Timer(stmt=stmt, setup=setup)
    res = timer.repeat(number=number, repeat=repeat)
    report('non persistent', res)

    owproxy = protocol.clone(base, persistent=True)
    res = timer.repeat(number=number, repeat=repeat)
    report('persistent', res)

    setup = "from __main__ import owproxy"
    if path.endswith('/'):
        stmt = 'owproxy.dir("{}")'.format(path)
    else:
        stmt = 'owproxy.read("{}")'.format(path)

    owproxy = base
    assert 'owproxy' in globals()
    try:
        eval(stmt, globals(), )
    except protocol.OwnetError as err:
        print(err)
        sys.exit(1)

    print(stmt)
    owproxy = protocol.clone(base, persistent=False)
    timer = timeit.Timer(stmt=stmt, setup=setup)
    res = timer.repeat(number=number, repeat=repeat)
    report('non persistent', res)

    owproxy = protocol.clone(base, persistent=True)
    res = timer.repeat(number=number, repeat=repeat)
    report('persistent', res)


if __name__ == '__main__':
    main()
