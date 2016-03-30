"""pyownet unit testing package"""

# public API
__all__ = ['HOST', 'PORT']

#
import sys
import os
if sys.version_info < (3, ):
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser

# setup config parser
config = ConfigParser()

# load config files
config.read(os.path.join(i, 'tests.ini') for i in __path__+['.'])

# export public API constants
HOST = config.get('server', 'host')
PORT = config.get('server', 'port')
