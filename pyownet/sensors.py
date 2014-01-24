# sensors

import collections

from pyownet import protocol

PropTuple = collections.namedtuple('PropTuple', ['tc', 'arr', 'nel', 'mode',
    'siz', 'pers'])

TCODE = dict(i=int, u=int, f=float, l=str, a=str, b=str, y=bool, d=str, 
    t=float, g=float, p=float)

def _parse_family(proxy, family):

    def walk(path):
        assert path.endswith('/')
        namespace = dict()
        pre = len(path)
        for i in proxy.dir(path):
            if not i.endswith('/'):
                pstr = proxy.read(i).split(',')[:-1]
                for j in (1,2,4):
                    pstr[j] = int(pstr[j])
                pt = PropTuple(*pstr)
                namespace[i[pre:]] = pt
            else:
                namespace[i[pre:-1]] = walk(i)
        return namespace

    path = '/structure/%s/' % family
    assert proxy.present(path)
    return walk(path)

def _sens_namespace(proxy, entity):

    def getter(i, cast):
        return lambda: cast(proxy.read(i))

    def walk(path,stru):
        assert path.endswith('/')
        pre = len(path)
        namespace = dict()
        for k, val in stru.iteritems():
            if isinstance(val, PropTuple):
                if val.pers != 'f':
                    namespace[k] = getter(path+k, TCODE[val.tc])
                else:
                    namespace[k] = getter(path+k, TCODE[val.tc])()
            else:
                assert isinstance(val, dict)
                namespace[k] = walk(path+k+'/', val)
        return namespace

    assert proxy.present(entity)
    assert entity.endswith('/')
    assert proxy.present(entity+'family')
    fam = proxy.read(entity+'family')
    stru = _parse_family(proxy, fam)
    namespace = walk(entity,stru) 
    assert namespace['family'] == fam
    return namespace
