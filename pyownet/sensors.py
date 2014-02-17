# sensors

#
# Copyright 2013, 2014 Stefano Miccoli
# 
# This python package is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import print_function

import posixpath
import types
import re

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

def _walk(proxy, root):

    assert root.endswith('/')
    ents = list(proxy.dir(root, slash=True))
    while ents:
        ent = ents.pop()
        if ent.endswith('/'):
            ents.extend(proxy.dir(ent))
        else:
            yield ent

def _fetch_structure(proxy, family):

    stru = dict()
    for i in _walk(proxy, '/structure/{0}/'.format(family)):
        name = i.split('/',3)[-1]
        stru[name] = Properties(proxy.read(i))
    return stru

def _sens_namespace(proxy, entity):

    rex = re.compile(r'.+\.[0-9]+')

    def getter(path, name, val):
        cast = _TYPE_CODE[val.type]
        read = lambda: cast(proxy.read(path))
        read.__doc__ = "returns %s as %s" % (path, cast)
        # fixme: str(name) is because in python 2 unicode is distinct form str
        read.__name__ = str(name)
        return read

    def walk(path):
        namespace = dict()
        pre = len(path)
        for i in proxy.dir(path):
            if i.endswith('/'):
                name = _pathname_mangle(i[pre:-1])
                namespace[name] = walk(i)
            else:
                name = _pathname_mangle(i[pre:])
                base = i.split('/', 2)[-1]
                if rex.match(base):
                    continue
                val = stru[base]
                assert isinstance(val, Properties)
                if val.mode not in ('ro', 'rw'):
                    continue
                if val.pers == 'f':
                    namespace[name] = getter(i, name, val)()
                else:
                    namespace[name] = staticmethod(getter(i, name, val))
        return namespace

    assert proxy.present(entity)
    assert proxy.present(posixpath.join(entity, 'family'))
    fam = proxy.read(posixpath.join(entity, 'family')).decode()
    stru = _fetch_structure(proxy, fam)
    namespace = walk(entity) 
    return namespace

def getsensor(proxy, path):

    ns = _sens_namespace(proxy, path)
    return metasensor(ns['type'], (_sensor, object), ns)()

def _main():
    def walk(prefix, s):
        for att in dir(s):
            fatt = getattr(s, att, None)
            if isinstance(fatt, types.FunctionType):
                try:
                    print(prefix, '{0}()'.format(att).ljust(13), fatt())
                except protocol.OwnetError as exp:
                    print(prefix, '{0}()'.format(att).ljust(13), exp)
            elif isinstance(fatt, str) and not fatt.startswith('__'):
                print(prefix, att.ljust(13), fatt)
            elif isinstance(fatt, _sensor):
                print(prefix, '{0}/'.format(att).ljust(13))
                walk('    ' + prefix, fatt)
    proxy = protocol.OwnetProxy()
    for i in proxy.dir():
        s = getsensor(proxy, i)
        print(s)
        walk('|--', s)
        print()

if __name__ == '__main__':
    _main()
