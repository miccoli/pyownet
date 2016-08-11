# sensors

#
# Copyright 2013, 2016 Stefano Miccoli
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

import sys
import types
import re
import weakref

from .protocol import bytes2str
from . import protocol

_STRUCT_DIR = protocol.PTH_STRUCTURE

# see http://owfs.org/index.php?page=structure-directory
_TYPE_CODE = dict(i=int, u=int, f=float,
                  l=bytes2str, a=bytes2str, b=bytes, y=bool,
                  d=bytes2str, t=float, g=float, p=float)
_PAGE = re.compile(r'.+\.[0-9]+')


class _metasensor(type):
    """recursive metaclass for handling sensors with subdirs"""

    def __new__(mcs, name, bases, namespace):
        for key, val in namespace.iteritems():
            if isinstance(val, dict):
                namespace[key] = _metasensor('subdir', bases, val)()
        return super(_metasensor, mcs).__new__(mcs, name, bases, namespace)


class _sensor(object):
    """mixin class for sensor objects"""

    def __str__(self):
        return "%s at %s" % (self.type, self.address)


class Properties(object):
    """properties class for records in '/structure/XX'"""

    def __init__(self, record):

        if not isinstance(record, (bytes, bytearray, )):
            raise TypeError('record must be binary')
        record = bytes2str(record)
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
        return 'Properties: %s, %2d, %2d, %s, %3d, %s' % (
            self.type, self.isarr, self.arrlen, self.mode, self.len, self.pers,
        )


def _pathname_mangle(path):
    """mangle owserver path names to obtain valid python variable names"""

    path = path.replace('-', '_')
    for suffix in ('.ALL', '/', ):
        if path.endswith(suffix):
            path = path[:-len(suffix)]
    return path


def _sens_namespace(proxy, entity, structure):
    """build a sensor namespace, to be used in metaclass _metasensor"""

    def getter(path, name, prop):
        """build and return a getter function"""
        cast = _TYPE_CODE[prop.type]
        read = lambda: cast(proxy.read(path))
        read.__doc__ = "returns %s as %s" % (path, cast)
        read.__name__ = name
        return read

    def rbuild(path):
        assert isinstance(path, str), "not a string '%s'" % path
        namespace = dict()
        pre = len(path)
        for i in proxy.dir(path, slash=True):
            name = _pathname_mangle(i[pre:])
            if i.endswith('/'):
                namespace[name] = rbuild(i)
            else:
                base = i.split('/', 2)[-1]
                if _PAGE.match(base):
                    continue
                prop = structure[base]
                assert isinstance(prop, Properties)
                if prop.mode not in ('ro', 'rw'):
                    continue
                if prop.pers == 'f':
                    namespace[name] = getter(i, name, prop)()
                else:
                    namespace[name] = staticmethod(getter(i, name, prop))
        return namespace

    assert entity.endswith('/')
    assert proxy.present(entity)
    namespace = rbuild(entity)
    return namespace


class Root(object):

    def __init__(self, hostport):

        if ':' in hostport:
            host, port = hostport.split(':')
            self.proxy = protocol.proxy(host, port)
        else:
            host = hostport
            self.proxy = protocol.proxy(host)

        # dicts for caching struct directory and sensors instances
        self._structure = dict()
        self._sensors = weakref.WeakValueDictionary()

    def __str__(self):
        return 'root at {0}'.format(self.proxy)

    def _walk(self, root):

        assert isinstance(root, str), repr(root)
        ents = [root]
        while ents:
            ent = ents.pop()
            if ent.endswith('/'):
                ents.extend(self.proxy.dir(ent, slash=True))
            else:
                yield ent, self.proxy.read(ent)

    def _getstructure(self, family):
        assert isinstance(family, str), repr(family)
        if family not in self._structure:
            self._structure[family] = dict(
                (i.split('/', 3)[-1], Properties(j))
                for i, j in self._walk(protocol.PTH_STRUCTURE + family + '/')
            )
        return self._structure[family]

    def scan(self):
        return self.proxy.dir('/', slash=True)

    def getsensor(self, path):

        if not path.endswith('/'):
            path += '/'

        if not self.proxy.present(path):
            raise ValueError('no such sensors')

        try:
            # requested sensor cached?
            return self._sensors[path]
        except KeyError:
            # no, go on.
            pass

        try:
            family = bytes2str(self.proxy.read(path + 'family'))
        except protocol.OwnetError:
            raise ValueError('{0} does not appear to be a sensor'.format(path))

        structure = self._getstructure(family)
        ns = _sens_namespace(self.proxy, path, structure)
        sensor = _metasensor(ns['type'], (_sensor, object), ns)()
        self._sensors[path] = sensor

        return sensor


def _main():

    try:
        hostport = sys.argv[1]
    except IndexError:
        hostport = 'localhost'
    root = Root(hostport)
    print('sensors on {0}'.format(root))
    for i in root.scan():
        print()
        s = root.getsensor(i)
        # test that weakref caching is working
        assert s is root.getsensor(i)
        assert s is root.getsensor(i)
        print(s)
        _recprint('|-', s, )


def _recprint(prefix, s):
    fprint = lambda s1, s2: print(prefix + '{0!s:.<14} {1!r}'.format(s1, s2))
    for att in dir(s):
        fatt = getattr(s, att, None)
        if isinstance(fatt, types.FunctionType):
            try:
                fprint(att + '()', fatt(), )
            except protocol.OwnetError as exp:
                fprint(att + '()', exp, )
        elif isinstance(fatt, str) and not fatt.startswith('__'):
            fprint(att, fatt)
        elif isinstance(fatt, _sensor):
            head = prefix + att + '/'
            print(head)
            _recprint(' ' * (len(head) - 1) + prefix, fatt)


if __name__ == '__main__':
    _main()
