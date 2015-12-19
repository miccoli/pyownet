"""floods owserver with non persistent requests

This program floods the owserver with non persistent dir() requests.
After about 16384 requests should fail with
'[Errno 49] Can't assign requested address'
"""

from __future__ import print_function

import itertools
import sys
if sys.version_info < (3, ):
    from urlparse import (urlsplit, )
else:
    from urllib.parse import (urlsplit, )

import pyownet
from pyownet import protocol


def main():
    assert len(sys.argv) == 2
    urlc = urlsplit(sys.argv[1], scheme='owserver', allow_fragments=False)
    host = urlc.hostname or 'localhost'
    port = urlc.port or 4304
    assert not urlc.path or urlc.path == '/'

    p = protocol.proxy(host, port, persistent=False)
    pid = 'unknown'
    ver = 'unknown'
    try:
        pid = int(p.read('/system/process/pid'))
        ver = p.read('/system/configuration/version').decode()
    except protocol.OwnetError:
        pass
    print(pyownet.__name__, pyownet.__version__, pyownet.__file__)
    print('proxy_obj: {}'.format(p))
    print('server info: pid {}, ver. {}'.format(pid, ver))

    freq = 1 << 12

    for i in itertools.count():
        try:
            _ = p.dir()
        except protocol.Error as exc:
            print('Iteration {0} raised exception: {1}'.format(i, exc))
            break
        None if i % freq else print('Iteration {}'.format(i))

if __name__ == '__main__':
    main()
