====================================================================
:mod:`pyownet.protocol` --- low level interface to owserver protocol
====================================================================

.. py:module:: pyownet.protocol
   :synopsis: low level interface to owserver protocol

.. warning::

   This software is still in alpha testing. Although it has been
   successfully used in production environments for more than 4 years,
   its API is not frozen yet, and could be changed.

The :mod:`pyownet.protocol` module is a low-level implementation of
the client side of the owserver protocol. Interaction with an owserver
takes place via a proxy object whose methods correspond to the
owserver protocol messages.

::

  >>> from pyownet import protocol
  >>> owproxy = protocol.proxy(host="server.example.com", port=4304)
  >>> owproxy.dir()
  ['/10.000010EF0000/', '/05.000005FA0100/', '/26.000026D90200/', '/01.000001FE0300/', '/43.000043BC0400/']
  >>> owproxy.read('/10.000010EF0000/temperature')
  b'         1.6'

.. _persistence:

Persistent vs. non persistent proxy objects.
--------------------------------------------

The owserver protocol presents two variants: *non persistent*
connection and *persistent* connection. In a *non persistent*
connection a network socket is bound and torn down for each
client-server message exchange; the protocol is stateless. For a
*persistent* connection the same socket is reused for subsequent
client-server interactions and the socket has to be torn down only
at the end of the session.  Note that there is no guarantee that a
persistent connection is granted by the server: if the server is not
willing to grant a persistent connection, the protocol requires a
fall-back towards a non persistent connection.

Correspondingly two different proxy object classes are implemented:
*non-persistent* and *persistent*.

* *Non-persistent* proxy objects are thread-safe, in the sense that
  different threads can use the same proxy object for concurrent
  access to the same owserver. At each method call of this class, a
  new socket is bound and torn down before the method return.

* *Persistent* proxy objects are not thread safe, in the sense that
  the same object cannot be used concurrently by different threads. If
  multithreaded use is desired, it is responsibility of the user to
  implement a proper locking mechanism.  On the first call to a
  method, a socket is bound to the owserver and kept open for reuse in
  the subsequent calls. It is responsibility of the user to explicitly
  close the connection at the end of a session.

In general, if performance is not an issue, it is safer to use
non-persistent connection proxies: the protocol is simpler to manage,
and usually the cost of creating a socket for each message is
negligible with respect to the 1-wire network response times.


Functions
---------

.. py:function:: proxy(host='localhost', port=4304, flags=0, \
                       persistent=False, verbose=False, )

   :param str host: host to contact
   :param int port: tcp port number to connect with
   :param int flags: protocol flag word to be ORed to each outgoing
                     message (see :ref:`flags`).
   :param bool persistent: whether the requested connection is
                           persistent or not.
   :param bool verbose: if true, print on ``sys.stdout`` debugging messages
                        related to the owserver protocol.
   :return: proxy object
   :raises pyownet.protocol.ConnError: if no connection can be established
        with ``host`` at ``port``.
   :raises pyownet.protocol.ProtocolError: if a connection can be established
        but the server does not support the owserver protocol.

   Proxy objects are created by this factory function; for
   ``persistent=False`` will be of class :class:`_Proxy` or
   :class:`_PersistentProxy` for ``persistent=True``

.. py:function:: clone(proxy, persistent=True)

   :param proxy: existing proxy object
   :param bool persistent: whether the new proxy object is persistent
                           or not
   :return: new proxy object

   There are costs involved in creating proxy objects (DNS lookups
   etc.). Therefore the same proxy object should be saved and reused
   in different parts of the program. The main purpose of this
   functions is to quickly create a new proxy object with the same
   properties of the old one, with only the persistence parameter
   changed. Typically this can be useful if one desires to use
   persistent connections in a multithreaded environment, as per
   the example below::

     from pyownet import protocol

     def worker(shared_proxy):
         with protocol.clone(shared_proxy, persistent=True) as newproxy:
             rep1 = newproxy.read(some_path)
             rep2 = newproxy.read(some_otherpath)
             # do some work

     owproxy = protocol.proxy(persistent=False)
     for i in range(NUM_THREADS):
         th = threading.Thread(target=worker, args=(owproxy, ))
         th.start()

   Of course, is persistence is not needed, the code
   could be more simple::

     from pyownet import protocol

     def worker(shared_proxy):
         rep1 = shared_proxy.read(some_path)
         rep2 = shared_proxy.read(some_otherpath)
         # do some work

     owproxy = protocol.proxy(persistent=False)
     for i in range(NUM_THREADS):
         th = threading.Thread(target=worker, args=(owproxy, ))
         th.start()


Proxy objects
-------------

Proxy objects are returned by the factory functions :func:`proxy` and
:func:`clone`: methods of the proxy object send messages to the
proxied server and return it's response, if any. They exists in two
versions: non persistent :class:`_Proxy` instances and persistent
:class:`_PersistentProxy` instances. The corresponding classes should
not be instantiated directly by the user, but only by the factory
functions.

.. py:class:: _Proxy

   Objects of this class follow the non persistent protocol: a new
   socket is created and connected to the owserver for each method
   invocation; after the server reply message is received, the socket
   is shut down. The implementation is thread-safe: different threads
   can use the same proxy object for concurrent access to the
   owserver.

   .. py:method:: ping()

       Send a *ping* message to owserver.

       :return: ``None``

       This is actually a no-op; this method could
       be used for verifying that a given server is accepting
       connections and alive.

   .. py:method:: present(path)

      Check if a node is present at path.

      :param str path: OWFS path
      :return: ``True`` if an entity is present at path, ``False`` otherwise
      :rtype: bool


   .. py:method:: dir(path='/', slash=True, bus=False)

      List directory content

      :param str path: OWFS path to list
      :param bool slash: ``True`` if directories should be marked with a
                         trailing slash
      :param bool bus: ``True`` if special directories should be listed
      :return: directory content
      :rtype: list

      Return a list of the pathnames of the entities that are direct
      descendants of the node at *path*, which has to be a
      directory::

        >>> owproxy = protocol.proxy()
        >>> owproxy.dir()
        ['/10.000010EF0000/', '/05.000005FA0100/', '/26.000026D90200/', '/01.000001FE0300/', '/43.000043BC0400/']
        >>> owproxy.dir('/10.000010EF0000/')
        ['/10.000010EF0000/address', '/10.000010EF0000/alias', '/10.000010EF0000/crc8', '/10.000010EF0000/errata/', '/10.000010EF0000/family', '/10.000010EF0000/id', '/10.000010EF0000/locator', '/10.000010EF0000/power', '/10.000010EF0000/r_address', '/10.000010EF0000/r_id', '/10.000010EF0000/r_locator', '/10.000010EF0000/scratchpad', '/10.000010EF0000/temperature', '/10.000010EF0000/temphigh', '/10.000010EF0000/templow', '/10.000010EF0000/type']

      If ``slash=True`` the pathnames of directories are marked by a
      trailing slash. If ``bus=True`` also special directories (like
      ``'/settings'``, ``'/structure'``, ``'/uncached'``) are listed.

   .. py:method:: read(path, size=MAX_PAYLOAD, offset=0)

      Read node at path

      :param str path: OWFS path
      :param int size: maximum length of data read
      :param int offset: offset at which read data
      :return: binary buffer
      :rtype: bytes

      Return the data read from node at path, which has not to be a
      directory.

      ::

        >>> owproxy = protocol.proxy()
        >>> owproxy.read('/10.000010EF0000/type')
        b'DS18S20'

      The ``size`` parameters can be specified to limit the maximum
      length of the data buffer returned; when ``offset > 0`` the
      first ``offset`` bytes are skipped. (In python slice notation,
      if ``data = read(path)``, then ``read(path, size, offset)``
      returns ``data[offset:offset+size]``.)

   .. py:method:: write(path, data, offset=0)

      Write data at path.

      :param str path: OWFS path
      :param bytes data: binary data to write
      :param int offset: offset at which write data
      :return: ``None``

      Writes binary ``data`` to node at ``path``; when ``offset > 0`` data
      is written starting at byte offset ``offset`` in ``path``.

      ::

        >>> owproxy = protocol.proxy()
        >>> owproxy.write('/10.000010EF0000/alias', b'myalias')

   .. py:method:: sendmess(msgtype, payload, flags=0, size=0, offset=0)

      Send message to owserver.

      :param int msgtype: message type code
      :param bytes payload: message payload
      :param int flags: message flags
      :param size int: message size
      :param offset int: message offset
      :return: owserver return code and reply data
      :rtype: ``(int, bytes)`` tuple

      This is a low level method meant as direct interface to the
      *owserver protocol,* useful for generating messages which are not
      covered by the other higher level methods of this class.

      This method sends a message of type ``msgtype`` (see
      :ref:`msgtypes`) with a given ``payload`` to the server;
      ``flags`` are ORed with the proxy general flags (specified in
      the ``flags`` parameter of the :func:`proxy` factory function),
      while ``size`` and ``offset`` are passed unchanged into the
      message header.

      The method returns a ``(retcode, data)`` tuple, where
      ``retcode`` is the server return code (< 0 in case of error) and
      ``data`` the binary payload of the reply message.

      ::

        >>> owproxy = protocol.proxy()
        >>> owproxy.sendmess(protocol.MSG_DIRALL, b'/', flags=protocol.FLG_BUS_RET)
        (0, b'/10.000010EF0000,/05.000005FA0100,/26.000026D90200,/01.000001FE0300,/43.000043BC0400,/bus.0,/uncached,/settings,/system,/statistics,/structure,/simultaneous,/alarm')
        >>> owproxy.sendmess(protocol.MSG_DIRALL, b'/nonexistent')
        (-1, b'')

.. py:class:: _PersistentProxy

   Objects of this class follow the persistent protocol, reusing the
   same socket connection for more than one method call.  When a
   method is called, it firsts check for an open connection: if none
   is found a socket is created and bound to the owserver. All
   messages are sent to the server with the :const:`FLG_PERSISTENCE`
   flag set; if the server grants persistence, the socket is kept
   open, otherwise the socket is shut down as for :class:`_Proxy`
   instances. In other terms if persistence is not granted there is an
   automatic fallback to the non persistent protocol.

   The use of the persistent protocol is therefore transparent to the
   user, with an important difference: if persistence is granted by
   the server, a socket connection is kept open to the owserver, after
   the last method call. It is the responsibility of the user to
   explicitly close the connection at the end of a session, to avoid
   server timeouts.

   :class:`_PersistentProxy` objects have all the methods of
   :class:`_Proxy`
   instances, plus a method for closing a connection.

   .. py:method:: close_connection()

      if there is an open connection, shuts down the socket; does
      nothing if no open connection is present.

   Note that after the call to :meth:`close_connection` the object can
   still be used: in fact a new method call will open a new socket
   connection.

   To avoid the need of explicitly calling the
   :meth:`close_connection` method, :class:`_PersistentProxy`
   instances support the context management protocol (i.e. the `with
   <https://docs.python.org/3/reference/compound_stmts.html#the-with-statement>`_
   statement.) When the ``with`` block is entered a socket connection
   is opened; the same socket connection is closed at the exit of the
   block. A typical usage pattern could be the following::

     owproxy = protocol.proxy(persistent=True)

     with owproxy:
         # here socket is bound to owserver
         # do work which requires to call owproxy methods
         res = owproxy.dir()
         # etc.

     # here socket is closed
     # do work that does not require owproxy access

     with owproxy:
         # again a connection is open
         res = owproxy.dir()
         # etc.

   In the above example, outside of the ``with`` blocks all socket
   connections to the owserver are guaranteed to be closed. Moreover
   the socket connection is opened when entering the block, even
   before the first call to a method, which could be useful for error
   handling.

   For non-persistent connections, entering and exiting the ``with``
   block context is a no-op.


Exceptions
----------

Base classes
^^^^^^^^^^^^

.. py:exception:: Error

   The base class for all exceptions raised by this module.

Concrete exceptions
^^^^^^^^^^^^^^^^^^^

.. py:exception:: OwnetError

   This exception is raised to signal an error return code by the
   owserver. This exception inherits also from the builtin `OSError`_
   and follows its semantics: it sets arguments ``errno``,
   ``strerror``, and, if available, ``filename``. Message errors are
   derived from the owserver introspection, by consulting the
   ``/settings/return_codes/text.ALL`` node.

.. _OSError: https://docs.python.org/3/library/exceptions.html#OSError

.. py:exception:: ConnError

   This exception is raised when a network connection to the owserver
   cannot be established, or a system function error occurs during
   socket operations. In fact it wraps the causing `OSError`_
   exception along with all its arguments, from which it inherits.

.. py:exception:: ProtocolError

   This exception is raised when a successful network connection is
   established, but the remote server does not speak the owserver
   network protocol or some other error occurred during the exchange
   of owserver messages.

.. py:exception:: MalformedHeader

   A subclass of :exc:`ProtocolError`: raised when it is impossible to
   decode the reply header received from the remote owserver.

.. py:exception:: ShortRead

   A subclass of :exc:`ProtocolError`: raised when the payload
   received from the remote owserver is too short.

.. py:exception:: ShortWrite

   A subclass of :exc:`ProtocolError`: raised when it is impossible to
   send the complete payload to the remote owserver.



Exception hierarchy
^^^^^^^^^^^^^^^^^^^

The exception class hierarchy for this module is:

.. code-block:: none

   pyownet.Error
    +-- pyownet.protocol.Error
         +-- pyownet.protocol.OwnetError
         +-- pyownet.protocol.ConnError
         +-- pyownet.protocol.ProtocolError
              +-- pyownet.protocol.MalformedHeader
              +-- pyownet.protocol.ShortRead
              +-- pyownet.protocol.ShortWrite


Constants
---------

.. py:data:: MAX_PAYLOAD

  Defines the maximum number of bytes that this module is willing to
  read in a single message from the remote owserver. This limit is
  enforced to avoid security problems with malformed headers. The limit
  is hardcoded to 65536 bytes. [#alpha]_

.. _msgtypes:

Message types
^^^^^^^^^^^^^

These constants can by passed as the ``msgtype`` argument to
:meth:`_Proxy.sendmess` method

.. see 'enum msg_classification' from ow_message.h

.. seealso:: `owserver message types
             <http://owfs.org/index.php?page=owserver-message-types>`_

.. py:data:: MSG_ERROR
.. py:data:: MSG_NOP
.. py:data:: MSG_READ
.. py:data:: MSG_WRITE
.. py:data:: MSG_DIR
.. py:data:: MSG_PRESENCE
.. py:data:: MSG_DIRALL
.. py:data:: MSG_GET
.. py:data:: MSG_DIRALLSLASH
.. py:data:: MSG_GETSLASH

.. _flags:

Flags
^^^^^

The module defines a number of constants, to be passed as the ``flags``
argument to :func:`proxy`. If more flags should apply, these have to
be ORed together: e.g. for reading temperatures in Kelvin and
pressures in Pascal, one should call::

   owproxy = protocol.proxy(flags=FLG_TEMP_K | FLG_PRESS_PA)

.. seealso:: `OWFS development site: owserver flag word
             <http://owfs.org/index.php?page=owserver-flag-word>`_


general flags
.............

.. py:data:: FLG_BUS_RET
.. py:data:: FLG_PERSISTENCE
.. py:data:: FLG_ALIAS
.. py:data:: FLG_SAFEMODE
.. py:data:: FLG_UNCACHED
.. py:data:: FLG_OWNET

temperature reading flags
.........................

.. py:data:: FLG_TEMP_C
.. py:data:: FLG_TEMP_F
.. py:data:: FLG_TEMP_K
.. py:data:: FLG_TEMP_R

pressure reading flags
......................

.. py:data:: FLG_PRESS_MBAR
.. py:data:: FLG_PRESS_ATM
.. py:data:: FLG_PRESS_MMHG
.. py:data:: FLG_PRESS_INHG
.. py:data:: FLG_PRESS_PSI
.. py:data:: FLG_PRESS_PA

sensor name formatting flags
............................

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

FICD are format codes defined as below:

======  ======================================================
format  interpretation
======  ======================================================
F       family code (1 byte) as hex string
I       device serial number (6 bytes) as hex string
C       Dallas Semiconductor 1-Wire CRC (1 byte) as hex string
D       a single dot character '.'
======  ======================================================

.. rubric:: Footnotes

.. [#alpha] Subject to change while package is in alpha phase.
