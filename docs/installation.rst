Installation
============

Source code
-----------

Source code for pyownet is hosted on GitHub:
https://github.com/miccoli/pyownet . The project is registered on
PyPI: https://pypi.python.org/pypi/pyownet .

Python version support
^^^^^^^^^^^^^^^^^^^^^^

The code base is written in Python 2, but Python 3 is fully supported,
and is the main developing language. Running the ``2to3`` tool will
generate valid and, whenever possible, idiomatic Python 3 code. The
present documentation refers to the Python 3 version of the package.

Explicitly supported versions are Python 2.6, 2.7, 3.3 through 3.6.

Install from PyPI
-----------------

The preferred installation method is from `PyPI`_ via `pip`_: ::

  pip install pyownet

This will install the :py:mod:`pyownet` package in the default
location.

If you are also interested in usage examples and tests you can
download the source package from the PyPI `downloads`_, unpack it, and
install::

  python setup.py install

In the source tree there will be ``example`` and ``test`` directories.

.. _PyPI: https://pypi.python.org/pypi/
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
