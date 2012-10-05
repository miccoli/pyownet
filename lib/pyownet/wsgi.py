"""wsgi app"""

__version__ = "$Revision: 305 $"
__revision__ = "$Id: __init__.py 305 2011-09-21 07:10:19Z miccoli $"
# $URL: https://data.mecc.polimi.it/svn/miccoli/pyownet/trunk/lib/pyownet/__init__.py $

import threading
import time
import pyownet.protocol

_UPD_FREQ = 30.0

class Application(object):

    def __init__(self, sensors, lim=25.0, step=5.0):

        self.sensors = sensors
        self.lim = lim
        self.step = step
        self.status = -1
        self.proxy = pyownet.protocol.OwnetProxy()
        thr = threading.Thread(target=self.updater, name="updater")
        thr.daemon = True
        thr.start()

    def __call__(self, env, start):
        start('200 OK', [('Content-type', 'text/plain'), ])
        yield("%d\n" % (self.status, ))

    def updater(self):
        while True:
            status = 0
            for i in self.sensors:
                try:
                    var = float(self.proxy.read(i))
                except pyownet.protocol.Error:
                    status = max(status, 1)
                    continue
                if var > self.lim:
                    status = max(status, 1 + int((var-self.lim)/self.step), )
            self.status = status 
            time.sleep(_UPD_FREQ)
