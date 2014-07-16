import unittest
from pyownet import protocol

from ConfigParser import ConfigParser

config = ConfigParser()

config.add_section('server')
config.set('server', 'host', 'localhost')
config.set('server', 'port', '4304')

config.read(['tests.ini'])

HOST = config.get('server', 'host')
PORT = config.get('server', 'port')


class TestProtocolModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.proxy = protocol.OwnetProxy(HOST, PORT)
        except protocol.ConnError as exc:
            raise RuntimeError('no owserver on %s:%s, got:%s' %
                               (HOST, PORT, exc))

    def test_ping(self):
        self.assertIsNone(self.proxy.ping())

    def test_present(self):
        self.assertIs(self.proxy.present('/'), True)
        self.assertIs(self.proxy.present('/nonexistent'), False)

    def test_dir_read(self):
        for i in self.proxy.dir(bus=False):
            self.assertTrue(self.proxy.present(i))
            self.assertTrue(self.proxy.present(i + 'type'))
            self.proxy.read(i + 'type')
            if self.proxy.present(i + 'temperature'):
                self.proxy.read(i + 'temperature')

    def test_exceptions(self):
        self.assertRaises(protocol.OwnetError, self.proxy.dir, '/nonexistent')
        self.assertRaises(protocol.OwnetError, self.proxy.read, '/')
        self.assertRaises(protocol.ConnError, protocol.OwnetProxy,
                          host='nonexistent.fake')
        self.assertRaises(TypeError, protocol._FromServerHeader, bad=0)
        self.assertRaises(TypeError, protocol._ToServerHeader, bad=0)
        self.assertRaises(TypeError, self.proxy.dir, 1)
        self.assertRaises(TypeError, self.proxy.write, '/', 1)
        self.assertRaises(TypeError, self.proxy.write, 1, b'abc')

if __name__ == '__main__':
    unittest.main()
