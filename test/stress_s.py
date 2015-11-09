import itertools
from pyownet import protocol
from . import (HOST, PORT)

p = protocol.proxy(HOST, PORT, persistent=False)
freq = 1 << 12

for i in itertools.count():
    try:
        c = p.dir()
    except protocol.Error as exc:
        print('Iteration {0} raised exception: {1}'.format(i, exc))
        break
    None if i % freq else print('Iteration {}'.format(i))
