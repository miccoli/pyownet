__revision__ = '$Id$'
__version__ = '$Revision$'

from distutils.core import setup

setup(name = 'pyownet',
      version = '0.2',
      description = 'python ownet client library',
      author = 'Stefano Miccoli',
      author_email = 'stefano.miccoli@polimi.it',
      package_dir = {'': 'lib', },
      py_modules = ['pyownet.protocol', ],
      scripts = [ 'scripts/status.py', 'scripts/digistate.py', ],
     )
