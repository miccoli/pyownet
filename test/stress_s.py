"""floods owserver with non persistent requests

This program floods the owserver with non persistent dir() requests.
After about 16384 requests should fail with
'[Errno 49] Can't assign requested address'
"""

from __future__ import print_function

import itertools
import pyownet
from pyownet import protocol
from . import (HOST, PORT)


def main():
    print(pyownet.__name__, pyownet.__version__, pyownet.__file__)
    p = protocol.proxy(HOST, PORT, persistent=False)
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
