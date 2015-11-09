import sys
if sys.version_info < (2, 7, ):
    import unittest2 as unittest
else:
    import unittest
import warnings

from pyownet import protocol
from . import (HOST, PORT)


def setUpModule():
    warnings.simplefilter('ignore', PendingDeprecationWarning)


class _TestProxyMix(object):
    # mixin class for testing proxy object functionality

    def setUp(self):
        try:
            getattr(self, 'proxy')
        except AttributeError:
            self.skipTest('no proxy available')

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
        self.assertRaises(TypeError, self.proxy.dir, 1)
        self.assertRaises(TypeError, self.proxy.write, '/', 1)
        self.assertRaises(TypeError, self.proxy.write, 1, b'abc')


class TestOwnetProxy(_TestProxyMix, unittest.TestCase, ):

    @classmethod
    def setUpClass(cls):
        try:
            cls.proxy = protocol.OwnetProxy(HOST, PORT)
        except protocol.ConnError as exc:
            raise unittest.SkipTest('no owserver on %s:%s, got:%s' %
                                    (HOST, PORT, exc))


class Test_Proxy(_TestProxyMix, unittest.TestCase, ):

    @classmethod
    def setUpClass(cls):
        try:
            cls.proxy = protocol.proxy(HOST, PORT, persistent=False)
        except protocol.ConnError as exc:
            raise unittest.SkipTest('no owserver on %s:%s, got:%s' %
                                    (HOST, PORT, exc))


class Test_PersistentProxy(_TestProxyMix, unittest.TestCase, ):

    @classmethod
    def setUpClass(cls):
        try:
            cls.proxy = protocol.proxy(HOST, PORT, persistent=True, )
        except protocol.ConnError as exc:
            raise unittest.SkipTest('no owserver on %s:%s, got:%s' %
                                    (HOST, PORT, exc))


class Test_clone_FT(Test_Proxy):

    def setUp(self):
        assert not isinstance(self.__class__.proxy, protocol._PersistentProxy)
        self.proxy = protocol.clone(self.__class__.proxy, persistent=True)

    def tearDown(self):
        self.proxy.close_connection()


class Test_clone_FF(Test_Proxy):

    def setUp(self):
        assert not isinstance(self.__class__.proxy, protocol._PersistentProxy)
        self.proxy = protocol.clone(self.__class__.proxy, persistent=False)


class Test_clone_TT(Test_PersistentProxy):

    def setUp(self):
        assert isinstance(self.__class__.proxy, protocol._PersistentProxy)
        self.proxy = protocol.clone(self.__class__.proxy, persistent=True)

    def tearDown(self):
        self.proxy.close_connection()


class Test_clone_TF(Test_PersistentProxy):

    def setUp(self):
        assert isinstance(self.__class__.proxy, protocol._PersistentProxy)
        self.proxy = protocol.clone(self.__class__.proxy, persistent=False)


class Test_misc(unittest.TestCase):

    def test_exceptions(self):
        self.assertRaises(protocol.ConnError, protocol.OwnetProxy,
                          host='nonexistent.fake')
        self.assertRaises(TypeError, protocol._FromServerHeader, bad=0)
        self.assertRaises(TypeError, protocol._ToServerHeader, bad=0)
        self.assertRaises(protocol.ConnError, protocol.proxy, HOST, -1)
        self.assertRaises(TypeError, protocol.clone, 1)

if __name__ == '__main__':
    unittest.main()
