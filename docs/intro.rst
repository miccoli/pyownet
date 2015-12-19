Introduction
============

pyownet is a pure Python package for interfacing to a 1-Wire
network via OWFS. A brief introduction to the main components with
which pyownet interacts is given below.

1-Wire
------

1-Wire® is a a single contact serial interface developed by Maxim
Integrated™. A typical 1-Wire network is composed by a master device
and a collection of slave devices/sensors. The master device is
usually connected to a host computer via a serial or USB interface,
but there exist also ethernet or other network adapters.

.. seealso::

   `1-Wire Maxim`_
       1-Wire technology brief from Maxim Integrated

   .. _1-Wire Maxim:
       https://www.maximintegrated.com/en/products/digital/one-wire.html

   `1-Wire Wikipedia <https://en.wikipedia.org/wiki/1-Wire>`_
       description of the 1-Wire bus system on Wikipedia


OWFS and the owserver protocol
------------------------------

The "1-Wire File System", in short OWFS, is a software system that
allows to access a 1-Wire bus via a supported master device. OWFS
comprises many different modules which offer different access
protocols to 1-Wire data: ``owhttpd`` (http), ``owftpd`` (ftp) and
``owfs`` (filesystem interface via FUSE). Since only a single program
can access the 1-Wire bus at one time, there is also a back end
component, ``owserver``, that arbitrates access to the bus from
multiple client processes. Client processes can query an ``owserver``
(the program) via network sockets speaking the 'owserver'
protocol. OWFS offers many language bindings for writing owserver
clients: among others c, java, perl, php, python, which can be found
in the OWFS source tree under the `module/ownet`_ directory.

.. _module/ownet:
   http://sourceforge.net/p/owfs/code/ci/master/tree/module/ownet/

.. seealso::

   `OWFS 1-Wire File System - development site <http://owfs.org/>`_
       official OWFS site


owserver protocol brief
.......................

The owserver protocol follows a client-server paradigm: the client
makes a connection to the listening socket of the ``owserver`` program
and sends a message. The server replies with another message, and then
either closes the connection or waits for other messages [#pers]_. The
default port 4304/tcp (and 4304/udp, although UDP is not used) is
`registered at the IANA`_ as *owserver* service for this purpose.

.. _registered at the IANA:
   https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml?search=4304#table-service-names-port-numbers

Both the client and server messages are composed by a fixed length
header and a variable length payload. The header structure is defined
in the OWFS source tree in file
``module/owlib/src/include/ow_message.h`` as::

  #include <stdint.h>

  /* message to owserver */
  struct server_msg {
        int32_t version;
        int32_t payload;
        int32_t type;
        int32_t control_flags;
        int32_t size;
        int32_t offset;
  };

  /* message to client */
  struct client_msg {
        int32_t version;
        int32_t payload;
        int32_t ret;
        int32_t control_flags;
        int32_t size;
        int32_t offset;
  };

  #define OWSERVER_PROTOCOL_VERSION   0

The ``version`` member is set to ``OWSERVER_PROTOCOL_VERSION``,
``payload`` is the payload length (in bytes), while
``server_msg.type`` is a constant that describes the type of request
made to the server (see also :ref:`msgtypes`). ``client_msg.ret`` is a
server return code (used to signal errors or abnormal situations)
while ``control_flags`` are used to control various aspects of the
owserver protocol (see also :ref:`flags`).

After the header the actual payload is transmitted, as a (binary)
stream of bytes (of length ``server_msg.payload`` or
``client_msg.payload``).

.. seealso::

   `owserver network protocol`_
       protocol specification

   .. _owserver network protocol:
       http://owfs.org/index.php?page=owserver-protocol


:py:mod:`pyownet` package contents
----------------------------------

To time :py:mod:`pyownet` comprises a single module
:py:mod:`pyownet.protocol`, which is a low-level implementation of the
client side of the owserver protocol. It can be considered a
replacement of the official OWFS module :py:mod:`ownet.connection` (to
be found in `module/ownet/python`_).

.. _module/ownet/python:
   http://sourceforge.net/p/owfs/code/ci/master/tree/module/ownet/python/




Although low-level, it's use is fairly simple, due
to the peculiar OWFS design, with it's file-system like structure.

A higher-level module :py:mod:`pyownet.sensors` is under development.

.. rubric:: Footnotes

.. [#pers] For a discussion of this type of keep-alive connection see
         :ref:`persistence`.
