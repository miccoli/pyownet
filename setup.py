from setuptools import setup
import re

with open('README.rst') as infile:
    long_description = infile.read()

regex = re.compile(
    r"__version__ = (?P<quot>['\"])(?P<ver>[\w.+-]+?)(?P=quot)$", )

with open('src/pyownet/__init__.py') as infile:
    for line in infile:
        version_match = regex.match(line)
        if version_match:
            __version__ = version_match.group('ver')
            break
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name = 'pyownet',
    version = __version__,
    description = 'python ownet client library',
    long_description = long_description,
    author = 'Stefano Miccoli',
    author_email = 'stefano.miccoli@polimi.it',
    url = 'https://github.com/miccoli/pyownet',
    license = 'GPL',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    package_dir = {'': 'src'},
    packages = ['pyownet', ],
    test_suite = "test.test_protocol",
    use_2to3 = True,
)
