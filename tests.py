import unittest
from pyownet import protocol

class TestProtocolModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.proxy = protocol.OwnetProxy()
        except protocol.ConnError as exc:
            raise RuntimeError('no owserver on localhost, got:%s' % exc)
  
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
        self.assertRaises(TypeError, self.proxy.dir, 1)
        self.assertRaises(TypeError, self.proxy.write, '/', 1)
        self.assertRaises(TypeError, self.proxy.write, 1, b'abc')

if __name__ == '__main__':
    unittest.main()

