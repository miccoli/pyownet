import unittest
from pyownet import protocol

class TestProtocolModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.proxy = protocol.OwnetProxy()
  
    def test_ping(self):
        self.assertIsNone(self.proxy.ping())

    def test_present(self):
        self.assertIs(self.proxy.present('/'), True)
        self.assertIs(self.proxy.present('/nonexistent'), False)

    def test_dir(self):
        for i in self.proxy.dir(bus=False):
            self.assertTrue(self.proxy.present(i))
            self.assertTrue(self.proxy.present(i + 'type'))
            stype = self.proxy.read(i + 'type')
            if self.proxy.present(i + 'temperature'):
                temp = self.proxy.read(i + 'temperature')
            else:
                temp = ''

    def test_exceptions(self):
        self.assertRaises(protocol.OwnetError, self.proxy.dir, '/nonexistent')
        self.assertRaises(protocol.OwnetError, self.proxy.read, '/')

if __name__ == '__main__':
    unittest.main()

