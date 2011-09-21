"""this module is a first try to implement the ownet protocol"""

import struct
import socket

MAX_PAYLOAD = 1024*1024

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

FLG_OWNET = 0x00000100
FLG_UNCACHED = 0x00000020
FLG_SAFEMODE = 0x00000010
FLG_ALIAS = 0x00000008
FLG_PERSISTENCE = 0x00000004
FLG_BUS_RET = 0x00000002


class Error(Exception):
    pass


class ShortRead(Error):
    pass


class ShortWrite(Error):
    pass


class DataError(Error):
    pass


class _Header(str):
    """base class for ownet protocol headers"""

    _format = struct.Struct(">iiiiii")
    hsize = _format.size

    def __new__(cls, *args, **kwargs):
        if args:
            msg = args[0]
            # FIXME check for args type and semantics
            assert len(args)==1
            assert not kwargs
            assert isinstance(msg, str)
            assert len(msg) == cls.hsize
            #
            vals = cls._format.unpack(msg)
        else:
            vals = tuple(map(kwargs.pop, cls._fields, cls._defaults))
            if kwargs:
                print dir()
                raise TypeError(
  "__new__() got an unexpected keyword argument '%s'" % kwargs.popitem()[0] )
            msg = cls._format.pack(*vals)
        self = super(_Header, cls).__new__(cls, msg)
        assert isinstance(vals, tuple)
        self._vals = vals
        return self

    def __repr__(self):
        repr = self.__class__.__name__ + '('
        repr += ', '.join(map(lambda x: '%s=%s' % x, 
                            zip(self._fields, self._vals)))
        repr += ')'
        return repr


class _addfieldprops(type):
    """metaclass for adding properties"""

    @staticmethod
    def _getter(i):
        return lambda x: x._vals[i]

    def __new__(mcs, name, bases, dict):
        for i, j in enumerate(dict['_fields']):
            dict[j] = property(mcs._getter(i))
        return type.__new__(mcs, name, bases, dict)


class ServerHeader(_Header):
    """client to server request header"""

    __metaclass__ = _addfieldprops
    _fields = ('version', 'payload', 'type', 'flags', 'size', 'offset')
    _defaults = (0, 0, MSG_NOP, FLG_OWNET, 1024, 0)


class ClientHeader(_Header):
    """server to client reply header"""

    __metaclass__ = _addfieldprops
    _fields = ('version', 'payload', 'ret', 'flags', 'size', 'offset')
    _defaults = (0, 0, 0, FLG_OWNET, 0, 0)


class OwnetClient(object):

    def __init__(self, hostport, verbose):
        
        self.verbose = verbose
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(hostport)
        if self.verbose:
            print self.sock.getsockname()

    def __del__(self):

        self.sock.close()

    def session(self, header, payload):
        """FIXME"""
        self.send_msg(header, payload)
        rep, data = self.read_msg()
        return rep, data

    def send_msg(self, header, payload):
        """
        FIXME
        """

        if self.verbose:
            print '->', repr(header)
            print '..', repr(payload)
        assert header.payload == len(payload)
        sent = self.sock.send(header + payload)
        if sent < len(header + payload):
            raise ShortWrite
        assert sent == len(header + payload), sent
        
    def read_msg(self):
        """
        FIXME
        """

        header = self.sock.recv(ClientHeader.hsize)
        if len(header) < ClientHeader.hsize:
            raise ShortRead('Error reading ClientHeader, got %s' % repr(header))
        header = ClientHeader(header)
        if self.verbose: 
            print '<-', repr(header)
        if header.version != 0 or header.payload > MAX_PAYLOAD:
            raise DataError('got malformed header: %s "%s"' % 
                                    (repr(header), header))
        if header.payload > 0:
            payload = self.sock.recv(header.payload)
            if len(payload) < header.payload:
                raise ShortRead('got %s' % repr(header)+':'+repr(payload))
            if self.verbose: 
                print '..', repr(payload)
            assert header.size <= header.payload
            payload = payload[:header.size]
        else:
            payload = ''
        return header, payload
    

class OwnetProxy(object):
    """proxy with owserver"""

    def __init__(self, host='localhost', port=4304, verbose=False):
        self._hostport = (host, port)
        self.verbose = verbose
        # check connection
        # FIXME
        # without timeout this may hang!
        assert self._session(ServerHeader(),'') == (ClientHeader(), '')

    def _session(self, header, payload):
        sess = OwnetClient(self._hostport, self.verbose)
        return sess.session(header, payload)

    def dir(self, path):
        """li = dir(path)"""
        # build message
        path += '\x00'
        sheader = ServerHeader(payload=len(path), type=MSG_DIRALLSLASH)
        # chat
        cheader, data = self._session(sheader, path)
        # check reply
        if cheader.ret < 0:
            raise DataError(repr(cheader))
        if data:
            return data.split(',')
        else:
            return []

    def read(self, path):
        """val = read(path)"""
        # build message
        path += '\x00'
        sheader = ServerHeader(payload=len(path), type=MSG_READ)
        # chat
        cheader, data = self._session(sheader, path)
        # chek reply
        if cheader.ret < 0:
            raise DataError(repr(cheader))
        return data


def test():
    proxy = OwnetProxy(verbose=True)
    proxy.dir('/')
    proxy.read('/26.B4FF64000000/temperature')

if __name__ == '__main__':
    test()
