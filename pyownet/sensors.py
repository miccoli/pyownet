# sensors

from __future__ import print_function

import posixpath
import types

from pyownet import protocol

_TYPE_CODE = dict(i=int, u=int, f=float, l=str, a=str, b=bytes, y=bool, 
    d=str, t=float, g=float, p=float)


class metasensor(type):

    def __new__(mcs, name, bases, namespace):
        for key, val in namespace.iteritems():
            if isinstance(val, dict):
                namespace[key] = metasensor('subdir', bases, val)()
        return super(metasensor, mcs).__new__(mcs, name, bases, namespace)


class _sensor(object):

    def __str__(self):
        return "%s at %s" % (self.type, self.address)


class Properties(object):
    
    def __init__(self, record):

        if not isinstance(record, str):
            raise TypeError('record must be a string')
        flds = record.split(',')
        if len(flds) < 7:
            raise ValueError('invalid record')

        self.type = flds[0]
        self.isarr = int(flds[1])
        self.arrlen = int(flds[2])
        self.mode = flds[3]
        self.len = int(flds[4])
        self.pers = flds[5]

    def __str__(self):
        return 'Properties: %s, %2d, %2d, %s, %3d, %s' % (self.type, 
            self.isarr, self.arrlen, self.mode, self.len, self.pers, )

def _pathname_mangle(path):
    path = path.replace('-', '_')
    path = path.replace('.ALL', '')
    return path

def _parse_structure(proxy, family):

    def walk(path):
        namespace = dict()
        pre = len(path)
        for i in proxy.dir(path):
            if i.endswith('/'):
                namespace[i[pre:-1]] = walk(i)
            else:
                namespace[i[pre:]] = Properties(proxy.read(i))
                #print(i.ljust(35), Properties(proxy.read(i)))
        return namespace

    path = '/structure/%s/' % family
    assert proxy.present(path)
    return walk(path)

def _sens_namespace(proxy, entity):

    def getter(path, name, val):
        cast = _TYPE_CODE[val.type]
        read = lambda: cast(proxy.read(path))
        read.__doc__ = "returns %s as %s" % (path, cast)
        # fixme: str(name) is because in python 2 unicode is distinct form str
        read.__name__ = str(name)
        return read

    def walk(path,stru):
        namespace = dict()
        for k, val in stru.iteritems():
            pk = posixpath.join(path, k)
            mk = _pathname_mangle(k)
            if isinstance(val, dict):
                namespace[mk] = walk(pk, val)
            else:
                assert isinstance(val, Properties)
                if val.mode not in ('ro', 'rw'):
                    continue
                if k.endswith('.0'):
                    continue
                if val.pers == 'f':
                    namespace[mk] = getter(pk, mk, val)()
                else:
                    namespace[mk] = staticmethod(getter(pk, mk, val))
        return namespace

    assert proxy.present(entity)
    assert proxy.present(posixpath.join(entity, 'family'))
    fam = proxy.read(posixpath.join(entity, 'family')).decode()
    stru = _parse_structure(proxy, fam)
    namespace = walk(entity, stru) 
    return namespace

def getsensor(proxy, path):

    ns = _sens_namespace(proxy, path)
    return metasensor(ns['type'], (_sensor, object), ns)()

def _test():
    def walk(prefix, s):
        for att in dir(s):
            fatt = getattr(s, att, None)
            if isinstance(fatt, types.FunctionType):
                try:
                    print(prefix, att.ljust(12), fatt())
                except protocol.OwnetError as exp:
                    print(prefix, att.ljust(12), exp)
            elif isinstance(fatt, str) and not fatt.startswith('__'):
                print(prefix, att.ljust(12), fatt)
            elif isinstance(fatt, _sensor):
                print(prefix, att.ljust(12))
                walk('    ' + prefix, fatt)
    proxy = protocol.OwnetProxy()
    for i in proxy.dir():
        s = getsensor(proxy, i)
        print(s)
        walk('|--', s)

if __name__ == '__main__':
    _test()
