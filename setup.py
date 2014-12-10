from pyownet import __version__

with open('README.rst') as file:
    long_description = file.read()

from distutils.core import setup
try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    # 2.x
    from distutils.command.build_py import build_py

setup(name = 'pyownet',
      version = __version__,
      packages = ['pyownet', ],
      description = 'python ownet client library',
      long_description = long_description,
      author = 'Stefano Miccoli',
      author_email = 'stefano.miccoli@polimi.it',
      url = 'https://github.com/miccoli/pyownet',
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Environment :: Other Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          ],
      cmdclass = {'build_py':build_py},
     )
