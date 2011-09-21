__revision__ = '$Id$'
__version__ = '$Revision$'

from distutils.core import setup

setup(name = 'pyownet',
      version = '0.0',
      description = 'python ownet client',
      author = 'Stefano Miccoli',
      author_email = 'stefano.miccoli@polimi.it',
      package_dir = {'': 'lib', },
      py_modules = ['pyownet.protocol', ],
      #scripts = [ 'scripts/purgereg.py', 'scripts/syncsub.py', ],
     )
