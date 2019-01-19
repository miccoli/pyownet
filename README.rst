pyownet: Python OWFS client library (owserver protocol)
=======================================================

.. image:: https://readthedocs.org/projects/pyownet/badge/?version=latest&style=flat
   :target: http://pyownet.readthedocs.io/en/latest/
   :alt: Package Documentation

.. image:: https://img.shields.io/pypi/v/pyownet.svg
   :target: https://pypi.python.org/pypi/pyownet
   :alt: Python Package Index version

Pyownet is a pure python package that allows network client access to
the `OWFS 1-Wire File System`_ via an `owserver`_ and the `owserver
network protocol`_, in short *ownet*.

The ``pyownet.protocol`` module is an implementation of the owserver
client protocol that exposes owserver messages as methods of a proxy
object::

    >>> owproxy = pyownet.protocol.proxy(host="owserver.example.com", port=4304)
    >>> owproxy.dir()
    ['/10.67C6697351FF/', '/05.4AEC29CDBAAB/']
    >>> owproxy.read('/10.67C6697351FF/temperature')
    '     91.6195'

Installation
------------

To install pyownet::

    $ pip install pyownet


Python version support
----------------------

The code base is written in Python 2, but Python 3 is fully supported,
and is the main developing language. Running the ``2to3`` tool will
generate valid and, whenever possible, idiomatic Python 3 code.

Explicitly supported versions are Python 2.7, 3.3 through 3.7.


Documentation
-------------

Full package documentation is available at
http://pyownet.readthedocs.io/en/latest/


.. _owserver: http://owfs.org/index.php?page=owserver_protocol
.. _owserver network protocol: http://owfs.org/index.php?page=owserver-protocol
.. _OWFS 1-Wire File System: http://owfs.org
