from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
if sys.version_info < (2, 7, ):
    import unittest2 as unittest
else:
    import unittest
import warnings

from pyownet import protocol
from . import (HOST, PORT, FAKEHOST, FAKEPORT)


def setUpModule():
    """global setup"""
    # no global setup needed, for now


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
        self.assertTrue(self.proxy.present('/'))
        self.assertFalse(self.proxy.present('/nonexistent'))

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

    def test_context(self):
        with self.proxy as owp:
            try:
                self.assertIsInstance(owp.conn, protocol._OwnetConnection)
            except AttributeError:
                pass
        try:
            self.assertIsNone(owp.conn)
        except AttributeError:
            pass


class TestOwnetProxy(_TestProxyMix, unittest.TestCase, ):

    @classmethod
    def setUpClass(cls):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
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
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.assertRaises(protocol.ConnError, protocol.OwnetProxy,
                              host='nonexistent.fake')
        self.assertRaises(protocol.ConnError, protocol.proxy,
                          host='nonexistent.fake')
        self.assertRaises(protocol.ConnError, protocol.proxy,
                          host=HOST, port=-1)
        self.assertRaises(protocol.ProtocolError, protocol.proxy,
                          host=FAKEHOST, port=FAKEPORT)
        self.assertRaises(TypeError, protocol.clone, 1)
        self.assertRaises(TypeError, protocol._FromServerHeader, bad=0)
        self.assertRaises(TypeError, protocol._ToServerHeader, bad=0)

    def test_str(self):
        # check edge conditions in which _OwnetConnection.__str__ could fail
        try:
            p = protocol.proxy(HOST, PORT, persistent=True)
        except protocol.Error as exc:
            self.skipTest('no owserver on %s:%s, got:%s' % (HOST, PORT, exc))
        p.ping()
        if p.conn:
            p.conn.shutdown()
            str(p.conn)  # could fail if not able to determine socket peername
        else:
            self.skipTest('unable to create a persistent connection')

if __name__ == '__main__':
    unittest.main()
