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
    name='pyownet',
    version=__version__,
    description='Python OWFS client library (owserver protocol)',
    long_description=long_description,
    author='Stefano Miccoli',
    author_email='stefano.miccoli@polimi.it',
    url='https://github.com/miccoli/pyownet',
    license='LGPLv3',
    keywords=['OWFS', ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Home Automation',
    ],
    package_dir={'': 'src'},
    packages=['pyownet', ],
    test_suite="tests.test_protocol",
    use_2to3=True,
)
