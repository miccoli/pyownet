# sensors

import posixpath

from pyownet import protocol

_TYPE_CODE = dict(i=int, u=int, f=float, l=str, a=str, b=bytearray, y=bool, 
    d=str, t=float, g=float, p=float)


class metasensor(type):

    def __new__(mcs, name, bases, namespace):
        #TODO: check for name space clashes, sanity checks
        for key, val in namespace.iteritems():
            if isinstance(val, dict):
                namespace[key] = metasensor('subdir', bases, val)()
        assert super(metasensor, mcs).__new__ is type.__new__
        return super(metasensor, mcs).__new__(mcs, name, bases, namespace)


class _mixsensor(object):

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
                #print i.ljust(35), Properties(proxy.read(i))
        return namespace

    path = '/structure/%s/' % family
    assert proxy.present(path)
    return walk(path)

def _sens_namespace(proxy, entity):

    def getter(path, name, val):
        cast = _TYPE_CODE[val.type]
        def read():
            return cast(proxy.read(path))
        read.__doc__ = "returns %s as %s" % (path, cast)
        read.__name__ = name
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
    fam = proxy.read(posixpath.join(entity, 'family'))
    stru = _parse_structure(proxy, fam)
    namespace = walk(entity,stru) 
    return namespace

def getsensor(proxy, path):

    ns = _sens_namespace(proxy, path)
    return metasensor(ns['type'], (_mixsensor, object), ns)()

def _test():
    proxy = protocol.OwnetProxy()
    for i in proxy.dir():
        print getsensor(proxy, i)

if __name__ == '__main__':
    _test()
