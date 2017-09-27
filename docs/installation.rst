Installation
============

Source code
-----------

Source code for pyownet is hosted on GitHub:
https://github.com/miccoli/pyownet . The project is registered on
PyPI: https://pypi.python.org/pypi/pyownet .

Python version support
^^^^^^^^^^^^^^^^^^^^^^

The code base is written in Python 2, but Python 3 is fully supported:
running the 2to3_ tool will generate valid and, whenever possible,
idiomatic Python 3 code. The Python 2 version should be considered
legacy: the present documentation refers only to the Python 3 version.

.. _2to3: https://docs.python.org/3/library/2to3.html#to3-automated-python-2-to-3-code-translation

Explicitly supported versions are Python 2.6, 2.7, 3.3 through 3.6.

Install from PyPI
-----------------

The preferred installation method is from PyPI_ via pip_: ::

  pip install pyownet

This will install the :py:mod:`pyownet` package in the default
location.

If you are also interested in usage examples and tests you can
download the source package from the PyPI downloads_, unpack it, and
install::

  python setup.py install

In the source tree there will be ``example`` and ``test`` directories.

.. _PyPI: https://pypi.python.org/pypi/pyownet
.. _pip: https://pip.pypa.io/en/stable/user_guide/#installing-packages
.. _downloads: https://pypi.python.org/pypi/pyownet#downloads

Install from GitHub
-------------------

The most complete source tree is kept on GitHub: ::

  git clone https://github.com/miccoli/pyownet.git
  cd pyownet
  python setup.py install

Usually the ``master`` branch should be aligned with the most recent
release, while there could be other feature branches active.

Reporting bugs
--------------

Please open an issue on the pyownet `issues page
<https://github.com/miccoli/pyownet/issues>`_.
