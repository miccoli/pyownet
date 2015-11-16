from __future__ import print_function
import sys
import timeit
import argparse
if sys.version_info < (3, ):
    from urlparse import (urlsplit, )
else:
    from urllib.parse import (urlsplit, )

import pyownet
from pyownet import protocol


def main():

    def report(name, res):
        scale = 1e3  # report times in ms
        print('** {:15}'.format(name), end=':')
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

    print(pyownet.__name__, pyownet.__version__, pyownet.__file__)

    try:
        base = protocol.proxy(host, port, persistent=False)
    except protocol.ConnError as exc:
        sys.exit('Error connecting to {}:{} {}'.format(host, port, exc))
    pid = 'unknown'
    ver = 'unknown'
    try:
        pid = int(base.read('/system/process/pid'))
        ver = base.read('/system/configuration/version').decode()
    except protocol.OwnetError:
        pass

    print('proxy_obj: {}'.format(base))
    print('server info: pid {}, ver. {}'.format(pid, ver))
    print()

    number = args.number
    repeat = args.repeat

    setup = "from __main__ import proxy_obj"
    if path.endswith('/'):
        stmt = 'proxy_obj.dir("{}")'.format(path)
    else:
        stmt = 'proxy_obj.read("{}")'.format(path)

    print('timeit:\n statement: {}\n number: {}\n repetitions: {}'.format(
        stmt, number, repeat))
    print()

    global proxy_obj

    proxy_obj = base
    assert 'proxy_obj' in globals()
    try:
        eval(stmt, globals(), )
    except protocol.OwnetError as err:
        print(err)
        sys.exit(1)

    timer = timeit.Timer(stmt=stmt, setup=setup)

    proxy_obj = protocol.clone(base, persistent=False)
    res = timer.repeat(number=number, repeat=repeat)
    report('non persistent', res)

    proxy_obj = protocol.clone(base, persistent=True)
    res = timer.repeat(number=number, repeat=repeat)
    report('persistent', res)


if __name__ == '__main__':
    main()
