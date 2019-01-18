Changelog
=========

v0.10.0.post1 (2019-01-19)
--------------------------

v0.10.0 re-licensed under LGPL v3

v0.10.0 (2016-03-30)
--------------------

Per call ``timeout`` API implemented.

- restructure ``proxy()`` factory to avoid circular ref. on saved exception
- modify ``_OwnetConnection`` to ensure that a persistent connection is
  closed on errors (relevant for timeouts and other connection errors)
- implemented explicit timeout on ownet protocol methods;
  raises ``OwnetTimeout``
- ``socket`` code reviewed and refactored
- wrap calls to socket methods in ``_OwnetConnection`` and raise
  ``ConnError`` in case of ``OSerror``'s (close #5)
- deprecated classes moved to ``pyownet.legacy`` module

v0.9.0 (2016-01-04)
-------------------

No major new features, API cleanup to ensure that connections are
properly closed. Functions that return binary data return ``bytes``.

- implement dummy context management protocol for ``_Proxy``
  for consitency with _PersistentProxy
- ``OwnetProxy`` class deprecated
- create a diagnostics directory ``./diags``
- move test suite from ``./test`` to ``./tests``
- ``pyownet.protocol._OwnetConnection.req()`` returns ``bytes`` and not
  ``bytearray``.
  This is due to a simplification in
  ``pyownet.protocol._OwnetConnection._read_socket()`` method.
- better connection logic in ``pyownet.protocol.proxy()`` factory:
  first connect or raise ``protocol.ConnError``,
  then test owserver protocol or raise ``protocol.ProtocolError``
- use relative imports in ``pyownet.protocol``
- ``./test`` and ``./examples`` minor code refactor
- ``.gitignore`` cleanup (use only project specific ignores)
- add ``__del__`` in ``_PersistentProxy`` to ensure connection is closed
- use ``with _OwnetConnection`` inside ``_Proxy`` to shutdown sockets
- implement context management protocol for ``_OwnetConnection`` to
  guarantee that connection is shutdown on exit
- py26 testing via ``unittest2``
- transform ``./test`` directory in package, so that common code
  (used for reading configuration files) can be shared more easily
- move ``./pyownet`` to ``./src/pyownet``
