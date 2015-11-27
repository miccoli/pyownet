FIXME
=====

- code in 
  https://github.com/miccoli/pyownet/blob/master/pyownet/protocol.py#L704
  is not straightforward.

  if ``pclass`` is persistent 

      ``owp = pclass(...)`` creates ``_OwnetConnection``, 
      could raise ``ConnError``

      ``owp.ping()`` will send ``MSG_NOP``, could raise ``ProtocolError`` 
      or ``ConnError``

  if ``pclass`` is not persistent

      ``owp = pclass(...)`` never fails

      ``owp.ping()`` will first open a connection, could raise ``ConnError``
      then send ``MSG_NOP``, could raise ``ProtocolError`` or ``ConnError``


  Better way to go

  1. Search logic always with ``_PersistentProxy``

  2. send ``MSG_NOP`` to check if server speakes owserver

  3. if persistence not requested clone a non persisitent proxy


- http://pyownet.readthedocs.org/en/latest/protocol.html#pyownet.protocol.proxy
  should document which types of exceptions can be raised

