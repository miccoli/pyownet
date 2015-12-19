"""stress_t.py --  a stress test for owserver

This programs parses an owserver URI, constructed in the obvious way:
'owserver://hostname:port/path' and recursively walks down
"""

from __future__ import print_function

import sys
import time
import argparse
if sys.version_info < (3, ):
    from urlparse import urlsplit
else:
    from urllib.parse import urlsplit

from pyownet import protocol

__all__ = ['main']


def stress(owproxy, root):

    def walkdir(path):
        try:
            subdirs = owproxy.dir(path, slash=False, bus=False)
        except protocol.OwnetError as error:
            if error.errno != 20:
                raise ValueError('Wrong error at dir({0}): {1}'
                                 .format(path, error))
            _ = owproxy.read(path)
            return 1
        else:
            num = 0
            for i in subdirs:
                num += walkdir(i)
            return num

    def walkread(path):
        try:
            _ = owproxy.read(path)
        except protocol.OwnetError as error:
            num = 0
            if error.errno != 21:
                raise ValueError('Wrong error at read({0}): {1}'
                                 .format(path, error))
            for i in owproxy.dir(path, slash=False, bus=False):
                num += walkread(i)
            return num
        else:
            return 1

    tic = time.time()
    n = walkdir(root)
    toc = time.time()
    print('walkdir({}) : {:.3f}s for {:d} nodes'.format(root, toc - tic, n))

    tic = time.time()
    n = walkread(root)
    toc = time.time()
    print('walkread({}): {:.3f}s for {:d} nodes'.format(root, toc - tic, n))


def main():
    """parse commandline arguments and print result"""

    #
    # setup command line parsing a la argpase
    #
    parser = argparse.ArgumentParser()

    # positional args
    parser.add_argument('uri', metavar='URI', nargs='?', default='/',
                        help='[owserver:]//hostname:port/path')

    #
    # parse command line args
    #
    args = parser.parse_args()

    #
    # parse args.uri and substitute defaults
    #
    urlc = urlsplit(args.uri, scheme='owserver', allow_fragments=False)
    assert urlc.fragment == ''
    if urlc.scheme != 'owserver':
        parser.error("Invalid URI scheme '{0}:'".format(urlc.scheme))
    if urlc.query:
        parser.error("Invalid URI, query component '?{0}' not allowed"
                     .format(urlc.query))
    try:
        host = urlc.hostname or 'localhost'
        port = urlc.port or 4304
    except ValueError as error:
        parser.error("Invalid URI: invalid net location '//{0}/'"
                     .format(urlc.netloc))

    #
    # create owserver proxy object
    #
    try:
        owproxy = protocol.proxy(host, port, persistent=True)
    except protocol.ConnError as error:
        print("Unable to open connection to '{0}:{1}'\n{2}"
              .format(host, port, error), file=sys.stderr)
        sys.exit(1)
    except protocol.ProtocolError as error:
        print("Protocol error, '{0}:{1}' not an owserver?\n{2}"
              .format(host, port, error), file=sys.stderr)
        sys.exit(1)

    stress(owproxy, urlc.path)

if __name__ == '__main__':
    main()
