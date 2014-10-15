====================================================================
:mod:`pyownet.protocol` --- low level interface to owserver protocol
====================================================================

.. py:module:: pyownet.protocol
   :synopsis: low level interface to owserver protocol

The :mod:`pyownet.protocol` module is a low-level implementation of
the ownet protocol. Interaction with an owserver takes place via a
proxy object whose methods correspond to ownet messages::

  >>> owproxy = pyownet.protocol.proxy(host="server.example.com", port=4304)
  >>> owproxy.dir()
  [u'/10.A7F1D92A82C8/', u'/05.D8FE434D9855/', u'/26.8CE2B3471711/']
  >>> owproxy.present('/10.A7F1D92A82C8/temperature')
  True
  >>> owproxy.read('/10.A7F1D92A82C8/temperature')
  '     6.68422'

Functions
---------

.. py:function:: proxy(host='localhost', port=4304, flags=0, \
                       persistent=False, verbose=False, )

   this factory function is used to create a proxy object.

   :param str host: host to contact
   :return: proxy object


Proxy object
------------

.. py:class:: _Proxy

   :class:`_Proxy` instances are returned by the :func:`proxy` factory
   function and should not be instatiated by the user.

   .. py:method:: sendmess(msgtype, payload, flags=0, size=0, offset=0)

   .. py:method:: ping()

      sends a `ping` message to owserver.

   .. py:method:: present(path)

      returns true if an entity is present at `path`

   .. py:method:: dir(path='/', slash=True, bus=False)

   .. py:method:: read(path[, size])

   .. py:method:: write(path, data)

.. py:class:: _PersistentProxy

   .. py:method:: close_connection()


Flags
-----

The module defines a number of constants, to be passed as the `flags`
argument to :func:`proxy`. If more flags should apply, these have to
be ORed togheter: e.g. for reading temperatures in Kelvin and
pressures in Pascal, one should call::

   owproxy = proxy(flags=FLG_TEMP_K | FLG_PRESS_PA)

.. seealso:: `OWFS development site: owserver flag word
             <http://owfs.org/index.php?page=owserver-flag-word>`_


general flags
^^^^^^^^^^^^^

.. py:data:: FLG_BUS_RET
.. py:data:: FLG_PERSISTENCE
.. py:data:: FLG_ALIAS
.. py:data:: FLG_SAFEMODE
.. py:data:: FLG_UNCACHED
.. py:data:: FLG_OWNET

temperature reading flags
^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:data:: FLG_TEMP_C
.. py:data:: FLG_TEMP_F
.. py:data:: FLG_TEMP_K
.. py:data:: FLG_TEMP_R

pressure reading flags
^^^^^^^^^^^^^^^^^^^^^^

.. py:data:: FLG_PRESS_MBAR
.. py:data:: FLG_PRESS_ATM
.. py:data:: FLG_PRESS_MMHG
.. py:data:: FLG_PRESS_INHG
.. py:data:: FLG_PRESS_PSI
.. py:data:: FLG_PRESS_PA

sensor name formatting flags
^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. py:data:: FLG_FORMAT_FDI

.. py:data:: FLG_FORMAT_FI

.. py:data:: FLG_FORMAT_FDIDC

.. py:data:: FLG_FORMAT_FDIC

.. py:data:: FLG_FORMAT_FIDC

.. py:data:: FLG_FORMAT_FIC

These flags govern the format of the 1-wire 64 bit addresses as
reported by OWFS:

============================  ==================
flag                          format
============================  ==================
:py:const:`FLG_FORMAT_FDIDC`  10.67C6697351FF.8D
:py:const:`FLG_FORMAT_FDIC`   10.67C6697351FF8D
:py:const:`FLG_FORMAT_FIDC`   1067C6697351FF.8D
:py:const:`FLG_FORMAT_FIC`    1067C6697351FF8D
:py:const:`FLG_FORMAT_FDI`    10.67C6697351FF
:py:const:`FLG_FORMAT_FI`     1067C6697351FF
============================  ==================

FICD are format designators defined as below:

======  ======================================================
format  interpretation
======  ======================================================
F       family code (1 byte) as hex string
I       device serial number (6 bytes) as hex string
C       Dallas Semiconductor 1-Wire CRC (1 byte) as hex string
D       a single dot character '.'
======  ======================================================

 
