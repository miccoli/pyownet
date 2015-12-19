#
# script to test bug #1
#
import sys

if sys.version_info < (3, ):
    from urlparse import (urlsplit, )
else:
    from urllib.parse import (urlsplit, )

from pyownet.protocol import OwnetProxy


def main():
    assert len(sys.argv) == 2
    urlc = urlsplit(sys.argv[1], scheme='owserver', allow_fragments=False)
    host = urlc.hostname or 'localhost'
    port = urlc.port or 4304
    path = urlc.path or '/'

    p = OwnetProxy(host, port, verbose=True)

    while True:
        ret = p.read(path)
        assert ret, "'%s'" % ret

if __name__ == '__main__':
    main()
