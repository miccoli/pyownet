"""ownet protocol implementation

This module provides classes to query an owserver via the ownet protocol. 
It is a pure python implementation, with no external dependencies.

A proxy object is provided that implements methods for the protocol 
commands.

>>> owproxy = OwnetProxy(host="owserver.example.com", port=4304)
>>> owproxy.ping()
>>> owproxy.dir()
['/10.67C6697351FF/', '/05.4AEC29CDBAAB/']
>>> owproxy.present('/10.67C6697351FF/temperature')
True
>>> owproxy.read('/10.67C6697351FF/temperature')
'     91.6195'
>>> owproxy.write('/10.67C6697351FF/alias', 'sensA')

The lowlevel OwnetConnection encapsulates all socket operations and 
interactions with the server.

"""

from __future__ import print_function

import struct
import socket
import collections

# see msg_classification from ow_message.h
MSG_ERROR = 0
MSG_NOP = 1
MSG_READ = 2
MSG_WRITE = 3
MSG_DIR = 4
MSG_PRESENCE = 6
MSG_DIRALL = 7
MSG_GET = 8
MSG_DIRALLSLASH = 9
MSG_GETSLASH = 10

# see http://owfs.org/index.php?page=owserver-flag-word
# and ow_parsedname.h
FLG_BUS_RET =     0x00000002
FLG_PERSISTENCE = 0x00000004
FLG_ALIAS =       0x00000008
FLG_SAFEMODE =    0x00000010
FLG_UNCACHED =    0x00000020
FLG_OWNET =       0x00000100

# look for 
# 'enum temp_type' in ow_temperature.h
# 'enum pressure_type' in ow_pressure.h
# 'enum deviceformat' in ow.h

FLG_TEMP_C =        0x00000000
FLG_TEMP_F =        0x00010000
FLG_TEMP_K =        0x00020000
FLG_TEMP_R =        0x00030000
MSK_TEMPSCALE =     0x00030000

FLG_PRESS_MBAR =    0x00000000
FLG_PRESS_ATM =     0x00040000
FLG_PRESS_MMHG =    0x00080000
FLG_PRESS_INHG =    0x000C0000
FLG_PRESS_PSI =     0x00100000
FLG_PRESS_PA =      0x00140000
MSK_PRESSURESCALE = 0x001C0000

FLG_FORMAT_FDI =    0x00000000 #  /10.67C6697351FF
FLG_FORMAT_FI =     0x01000000 #  /1067C6697351FF
FLG_FORMAT_FDIDC =  0x02000000 #  /10.67C6697351FF.8D
FLG_FORMAT_FDIC  =  0x03000000 #  /10.67C6697351FF8D
FLG_FORMAT_FIDC =   0x04000000 #  /1067C6697351FF.8D
FLG_FORMAT_FIC =    0x05000000 #  /1067C6697351FF8D
MSK_DEVFORMAT =     0xFF000000

# internal constants

# socket timeout (s)
_SCK_TIMEOUT = 2.0
# do not attempt to read messages bigger than this (bytes)
_MAX_PAYLOAD = 65536

def str2bytez(s):
    "transform string to zero-terminated bytes"
    return s.encode() + b'\x00'

class _dummy(collections.Sequence):
    # dummy list, every item is an empty string
    __len__ = lambda self: 0
    __getitem__ = lambda self, i: ''

#
# exceptions
#

class Error(Exception):
    """Base class for all module errors"""
    pass


class ConnError(Error, IOError):
    """Connection failed"""
    pass


class ShortRead(Error):
    pass


class ShortWrite(Error):
    pass


class ProtocolError(Error):
    pass


class OwnetError(Error, EnvironmentError):
    pass


#
# classes
#

class _addfieldprops(type):
    """metaclass for adding properties"""

    @staticmethod
    def _getter(i):
        return lambda x: x._vals[i]

    def __new__(mcs, name, bases, namespace):
        if '_format' in namespace:
            assert '_fields' in namespace
            assert '_defaults' in namespace
            assert len(namespace['_defaults']) == len(namespace['_fields'])

            namespace['_struct'] = struct.Struct(namespace['_format'])
            namespace['header_size'] = namespace['_struct'].size
            for i, key in enumerate(namespace['_fields']):
                assert key not in namespace
                namespace[key] = property(mcs._getter(i))
            if __debug__:
                try:
                    namespace['_struct'].pack(*namespace['_defaults'])
                except struct.error as exp:
                    raise AssertionError('Unable to pack _defaults: %s' % exp)

        return super(_addfieldprops, mcs).__new__(mcs, name, bases, namespace)


class _Header(bytes):
    """abstract header class, obtained as a 'bytes' subclass

    should not be instantiated directly"""

    __metaclass__ = _addfieldprops

    @classmethod
    def _parse(cls, *args, **kwargs):
        if args:
            msg = args[0]
            # FIXME check for args type and semantics
            assert len(args)==1
            assert not kwargs
            assert isinstance(msg, bytes)
            assert len(msg) == cls.header_size
            #
            vals = cls._struct.unpack(msg)
        else:
            vals = tuple(map(kwargs.pop, cls._fields, cls._defaults))
            if kwargs:
                raise TypeError(
  "constructor got unexpected keyword argument '%s'" % kwargs.popitem()[0] )
            msg = cls._struct.pack(*vals)
        assert isinstance(msg, bytes)
        assert isinstance(vals, tuple)
        return msg, vals

    def __repr__(self):
        repr = self.__class__.__name__ + '('
        repr += ', '.join('%s=%s' % x for x in zip(self._fields, self._vals))
        repr += ')'
        return repr


    def __new__(cls, *args, **kwargs):
 
        #if cls is _Header:
        #    raise TypeError("_Header class may not be instantiated")
        msg, vals = cls._parse(*args, **kwargs)
        self = super(_Header, cls).__new__(cls, msg)
        self._vals = vals
        return self


class _ToServerHeader(_Header):
    """client to server request header"""

    _format = '>iiiiii'
    _fields = ('version', 'payload', 'type', 'flags', 'size', 'offset')
    _defaults = (0, 0, MSG_NOP, FLG_OWNET, 0, 0)


class _FromServerHeader(_Header):
    """server to client reply header"""

    _format = '>iiiiii'
    _fields = ('version', 'payload', 'ret', 'flags', 'size', 'offset')
    _defaults = (0, 0, 0, FLG_OWNET, 0, 0)


class OwnetConnection(object):
    """This class encapsulates a connection to an owserver"""

    def __init__(self, sockaddr, family=socket.AF_INET, verbose=False):
        "establish a connection with server at sockaddr"
        
        self.verbose = verbose
        self.socket = socket.socket(family, socket.SOCK_STREAM)
        self.socket.settimeout(_SCK_TIMEOUT)
        self.socket.connect(sockaddr)
        if self.verbose:
            print(self.socket.getsockname(), '->', self.socket.getpeername())

    def shutdown(self):
        "shutdown connection"
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def req(self, type, payload, flags, size=0, offset=0):
        "send message to server and return response"

        tohead = _ToServerHeader(payload=len(payload), type=type, flags=flags, 
            size=size, offset=offset)
        self._send_msg(tohead, payload)
        fromhead, data = self._read_msg()
        return fromhead.ret, fromhead.flags, data

    def _send_msg(self, header, payload):
        "send message to server"
        if self.verbose:
            print('->', repr(header))
            print('..', repr(payload))
        assert header.payload == len(payload)
        sent = self.socket.send(header + payload)
        if sent < len(header + payload):
            raise ShortWrite()
        assert sent == len(header + payload), sent
        
    def _read_msg(self):
        "read message from server"
        header = self.socket.recv(_FromServerHeader.header_size)
        if len(header) < _FromServerHeader.header_size:
            raise ShortRead('Error reading header, got %s' % repr(header))
        assert(len(header) == _FromServerHeader.header_size)
        header = _FromServerHeader(header)
        if self.verbose: 
            print('<-', repr(header))
        if header.version != 0:
            raise ProtocolError('got malformed header: %s "%s"' % 
                                    (repr(header), header))
        if header.payload > _MAX_PAYLOAD:
            raise ProtocolError('huge data, unwilling to read: %s "%s"' %
                                    (repr(header), header))
        if header.payload > 0:
            payload = self.socket.recv(header.payload)
            if len(payload) < header.payload:
                raise ShortRead('got %s' % repr(header)+':'+repr(payload))
            if self.verbose: 
                print('..', repr(payload))
            assert header.size <= header.payload
            payload = payload[:header.size]
        else:
            payload = bytes()
        return header, payload


class OwnetProxy(object):
    """Objects of this class define methods to query a given owserver"""

    def __init__(self, host='localhost', port=4304, flags=0, 
                 verbose=False, ):
        """return an ownet proxy object bound at (host, port); default is
        (localhost, 4304). 'flags' are or-ed in the headr of each query.
        If verbose is True, details on each sent and received packed is 
        printed on stdout.
        """ 

        # resolve host name/port
        try:
            gai = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
        except socket.gaierror as exp:
            raise ConnError(*exp.args)

        # gai is a list of tuples, search for the first working one
        lastexp = None
        for (family, _, _, _, sockaddr) in gai:
            try:
                conn = OwnetConnection(sockaddr, family, verbose)
            except socket.error as lastexp:
                # not working, go over to next sockaddr
                continue
            else:
                # ok, this is working, stop searching
                break
        else:
            # no working (sockaddr, family) found: raise error
            assert isinstance(lastexp, socket.error)
            assert isinstance(lastexp, IOError)
            raise ConnError(*lastexp.args)
        
        # here we have an open connection, close for now
        conn.shutdown()

        self._sockaddr, self._family = sockaddr, family

        self.verbose = verbose
        self.flags = flags

        # check if owserver on the line
        self.ping()

        #self.errmess = _dummy()
        # fetch errcodes array from owserver
        errcodes = '/settings/return_codes/text.ALL'
        assert self.present(errcodes)
        self.errmess = self.read(errcodes).decode().split(',')

    def sendmess(self, type, payload, flags=0, size=0, offset=0):
        """ retcode, data = sendmess(type, payload)
        send generic message and returns retcode, data
        """

        flags |= self.flags

        try:
            conn = OwnetConnection(self._sockaddr, self._family, 
                       self.verbose)
            ret, _, data = conn.req(type, payload, flags, size, offset)
            conn.shutdown()
        except IOError as exp:
            raise ConnError(*exp.args)

        return ret, data

    def ping(self):
        "sends a NOP packet and waits response; returns None"
        ret, data =  self.sendmess(MSG_NOP, bytes())
        if (ret, data) != (0, bytes()):
            raise OwnetError(-ret, self.errmess[-ret])

    def present(self, path):
        "returns True if there is an entity as path"

        ret, data = self.sendmess(MSG_PRESENCE, str2bytez(path))
        assert ret <= 0
        assert len(data) == 0
        if ret < 0:
            return False
        else:
            return True

    def dir(self, path='/', slash=True, bus=False):
        "list entities at path"

        if slash:
            msg = MSG_DIRALLSLASH
        else:
            msg = MSG_DIRALL
        if bus:
            flags = self.flags | FLG_BUS_RET
        else:
            flags = self.flags & ~FLG_BUS_RET

        ret, data = self.sendmess(msg, str2bytez(path), flags)
        if ret < 0:
            raise OwnetError(-ret, self.errmess[-ret], path)
        if data:
            return data.decode().split(',')
        else:
            return []

    def read(self, path, size=_MAX_PAYLOAD):
        "read data at path"

        if size > _MAX_PAYLOAD:
            raise ValueError("size cannot exceed < %d" % _MAX_PAYLOAD)

        ret, data = self.sendmess(MSG_READ, str2bytez(path), size=size)
        if ret < 0:
            raise OwnetError(-ret, self.errmess[-ret], path)
        return data

    def write(self, path, data):
        "write data at path"

        assert isinstance(bytes, data)
        ret, rdata = self.sendmess(MSG_WRITE, str2bytez(path)+data, 
            size=len(data))
        assert len(rdata) == 0
        if ret < 0:
            raise OwnetError(-ret, self.errmess[-ret], path)

def _test():
    proxy = OwnetProxy()
    proxy.ping()
    assert not proxy.present('/nonexistent')
    sensors = proxy.dir('/',bus=False)
    for j,i in enumerate(sensors):
        assert proxy.present(i), i
        stype = proxy.read(i + 'type')
        if proxy.present(i + 'temperature'):
            temp = proxy.read(i + 'temperature')
        else:
            temp = ''
        print(i, stype, temp)

if __name__ == '__main__':
    _test()
