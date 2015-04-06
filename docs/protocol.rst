====================================================================
:mod:`pyownet.protocol` --- low level interface to owserver protocol
====================================================================

.. py:module:: pyownet.protocol
   :synopsis: low level interface to owserver protocol

.. warning::

   This software is still in alpha testing. Altough it has been
   sucessfully used in production environments for more than 4 years,
   its API is not frozen yet, and could be changed.

The :mod:`pyownet.protocol` module is a low-level implementation of
the client side of the owserver protocol. Interaction with an owserver
takes place via a proxy object whose methods correspond to ownet
messages::

  >>> from pyownet import protocol
  >>> owproxy = protocol.proxy(host="server.example.com", port=4304)
  >>> owproxy.dir()
  [u'/10.A7F1D92A82C8/', u'/05.D8FE434D9855/', u'/26.8CE2B3471711/']
  >>> owproxy.present('/10.A7F1D92A82C8/temperature')
  True
  >>> owproxy.read('/10.A7F1D92A82C8/temperature')
  '     6.68422'

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
  multithread use is desired, it is responsibility of the user to
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
   persistent connections in a multi-threaded environment, as per
   example below. ::

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
   could be more simple: ::

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

      sends a *ping* message to owserver and returns ``None``. This is
      actually a no-op, and no response is expected; this method could
      be used for verifying that a given server is accepting
      connections.

   .. py:method:: present(path)

      returns ``True`` if an entity is present at *path*.

   .. py:method:: dir(path='/', slash=True, bus=False)

      returns a list of the pathnames of the entities that are direct
      descendants of the node at *path*, which has to be a
      directory. ::

	>>> p = protocol.proxy()
	>>> p.dir('/')
	[u'/10.A7F1D92A82C8/', u'/05.D8FE434D9855/', u'/26.8CE2B3471711/', u'/01.98542F112D05/']
	>>> p.dir('/01.98542F112D05/')
	[u'/01.98542F112D05/address', u'/01.98542F112D05/alias', u'/01.98542F112D05/crc8', u'/01.98542F112D05/family', u'/01.98542F112D05/id', u'/01.98542F112D05/locator', u'/01.98542F112D05/r_address', u'/01.98542F112D05/r_id', u'/01.98542F112D05/r_locator', u'/01.98542F112D05/type']

      If ``slash=True`` the pathnames of directories are marked by a
      trailing slash. If ``bus=True`` also special directories (like
      ``/settings/``, ``/structure/``, ``/uncached/``) are listed.

   .. py:method:: read(path, size=MAX_PAYLOAD, offset=0)

      returns the data read from node at path, which has not to be a
      directory. ::

	>>> p = protocol.proxy()
	>>> p.read('/01.98542F112D05/type')
	'DS2401'

      The ``size`` parameters can be specified to limit the maximum
      length of the data buffer returned; when ``offset > 0`` the
      first ``offset`` bytes are skipped. (In python slice notation,
      if ``data = read(path)``, then ``read(path, size, offset)``
      returns ``data[offset:offset+size]``.)

   .. py:method:: write(path, data, offset=0)

      writes binary ``data`` to node at path; when ``offset > 0`` data
      is written starting at byte offset ``offset`` in ``path``. ::

	>>> p = protocol.proxy()
	>>> p.write('01.98542F112D05/alias', b'aaa')

   .. py:method:: sendmess(msgtype, payload, flags=0, size=0, offset=0)

      is a low level method meant as direct interface to the *owserver
      protocol* useful for generating messages which are not covered
      by the other higher level methods of this class.

      This method sends a message of type ``msgtype`` (see
      :ref:`msgtypes`) with a given ``payload`` to the server;
      ``flags`` are ORed with the proxy general flags (specified in
      the ``flags`` parameter of the :func:`proxy` factory function),
      while ``size`` and ``offset`` are passed unchanged into the
      message header.

      The method returns a ``(retcode, data)`` tuple, where
      ``retcode`` is the server return code (< 0 in case of error) and
      ``data`` the binary payload of the reply message. ::

	>>> p = protocol.proxy()
	>>> p.sendmess(MSG_DIRALL, '/', flags=FLG_BUS_RET)
	(0, '/10.A7F1D92A82C8,/05.D8FE434D9855,/26.8CE2B3471711,/01.98542F112D05,/bus.0,/uncached,/settings,/system,/statistics,/structure,/simultaneous,/alarm')
	>>> p.sendmess(MSG_DIRALL, '/nonexistent')
	(-1, '')

.. py:class:: _PersistentProxy

   Objects of this class follow the persistent protocol, reusing the
   same socket connection for more than one method
   call. :class:`_PersistentProxy` instances are created with a closed
   connection to the owserver. When a method is called, it firsts
   check for an open connection: if none is found a socket is created
   and bound to the owserver. All messages are sent to the server with
   the :const:`FLG_PERSISTENCE` flag set; if the server grants
   persistence, the socket is kept open, otherwise the socket is shut
   down before the method return.

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

   To facilitate the use of the :meth:`close_connection`, method
   :class:`_PersistentProxy` objects support the context management
   protocol (i.e. the `with
   <https://docs.python.org/2.7/reference/compound_stmts.html#the-with-statement>`_
   statement.) When the ``with`` block is entered a socket connections
   is opened; the same socket connection is closed at the exit of the
   block. A typical usage pattern could be the following. ::

     owproxy = protocol.proxy(persistent=True)

     with owproxy:
	 # call methods of owproxy
	 ...

     # do some work which does not require owproxy

     with owproxy:
	 # call methods of owproxy
	 ...

   In the above example, outside of the ``with`` blocks all socket
   connections to the owserver are guaranteed to be closed. Moreover
   the socket connection is opened when entering the block, even
   before the first call to a method, which could be useful for error
   handling.


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

FICD are format designators defined as below:

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
