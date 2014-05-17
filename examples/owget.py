"""owget.py -- a pyownet implementation of owget

This small example shows how to implement a work-a-like of owget in
module owshell from owfs.

This programs parses an owserver URI, constructed in the obvious way:
'owserver://hostname:port/path' and prints the corresponding state.
If 'path' ends with a slash a DIR operation is executed, otherwise a READ.

The URI scheme 'owserver:' is optional. For 'hostname:port' the default
is 'localhost:4304'

Usage examples:

python owget.py //localhost:14304/
python owget.py //localhost:14304/26.000026D90200/
python owget.py -K //localhost:14304/26.000026D90200/temperature

Caution:
'owget.py //localhost:14304/26.000026D90200' or
'owget.py //localhost:14304/26.000026D90200/temperature/' yield an error

"""

from __future__ import print_function

import argparse
from urlparse import urlsplit
import collections
from binascii import hexlify

from pyownet.protocol import (OwnetProxy, ConnError, ProtocolError, OwnetError)
import pyownet.protocol as proto

__all__ = ['main']

def main():
    """parse commandline arguments and print result"""

    #
    # setup command line parsing a la argpase
    #
    parser = argparse.ArgumentParser()

    # positional args
    parser.add_argument('uri', metavar='URI', nargs='?', default='/',
        help='[owserver:]//server:port/entity')

    # optional args for temperature scale
    parser.set_defaults(t_flags=proto.FLG_TEMP_C)
    tempg = parser.add_mutually_exclusive_group()
    tempg.add_argument('-C', '--Celsius', const=proto.FLG_TEMP_C,
        help='Celsius(default) temperature scale',
        dest='t_flags', action='store_const', )
    tempg.add_argument('-F', '--Fahrenheit', const=proto.FLG_TEMP_F,
        help='Fahrenheit temperature scale',
        dest='t_flags', action='store_const', )
    tempg.add_argument('-K', '--Kelvin', const=proto.FLG_TEMP_K,
        help='Kelvin temperature scale',
        dest='t_flags', action='store_const', )
    tempg.add_argument('-R', '--Rankine', const=proto.FLG_TEMP_R,
        help='Rankine temperature scale',
        dest='t_flags', action='store_const', )

    # optional arg for address format
    fcodes = collections.OrderedDict((
        ('f.i', proto.FLG_FORMAT_FDI),
        ('fi', proto.FLG_FORMAT_FI),
        ('f.i.c', proto.FLG_FORMAT_FDIDC),
        ('f.ic', proto.FLG_FORMAT_FDIC),
        ('fi.c', proto.FLG_FORMAT_FIDC),
        ('fic', proto.FLG_FORMAT_FIC), ))
    parser.set_defaults(format='f.i')
    parser.add_argument('-f', '--format', choices=fcodes,
        help='format for 1-wire unique serial IDs display')

    # optional arg for output format
    parser.add_argument('--hex', action='store_true',
        help='write read data in hex format')

    #
    # parse command line args
    #
    args = parser.parse_args()

    #
    # parse args.uri and substitute defaults
    #
    urlc = urlsplit(args.uri, scheme='owserver', allow_fragments=False)
    if urlc.scheme != 'owserver':
        parser.error("Invalid URI scheme '{}:'".format(urlc.scheme))
    assert not urlc.fragment
    if urlc.query:
        parser.error("Invalid URI '{}', "
            "no query component allowed".format(args.uri))
    host = urlc.hostname or 'localhost'
    port = urlc.port or 4304

    #
    # create owserver proxy object
    #
    try:
        proxy = OwnetProxy(host, port, flags=args.t_flags|fcodes[args.format])
    except (ConnError, ProtocolError) as error:
        parser.exit(status=1, message=str(error)+'\n')

    try:
        if urlc.path.endswith('/'):
            for entity in proxy.dir(urlc.path, bus=True):
                print(entity)
        else:
            data = proxy.read(urlc.path)
            if args.hex:
                data = hexlify(data)
            print(data, end='')
    except OwnetError as error:
        parser.exit(status=1, message=str(error)+'\n')

if __name__ == '__main__':
    main()
