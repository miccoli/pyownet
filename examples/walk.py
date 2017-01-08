"""walk.py -- a pyownet implementation of owget

This implementation is for python 2.X

This programs parses an owserver URI, constructed in the obvious way:
'owserver://hostname:port/path' and prints all nodes reachable below it.

The URI scheme 'owserver:' is optional. For 'hostname:port' the default
is 'localhost:4304'

Usage examples:

python walk.py //localhost:14304/
python walk.py //localhost:14304/26.000026D90200/
python walk.py -K //localhost:14304/26.000026D90200/temperature

Caution:
'owget.py //localhost:14304/26.000026D90200' or
'owget.py //localhost:14304/26.000026D90200/temperature/' yield an error

"""

from __future__ import print_function

import sys
import argparse
if sys.version_info < (3, ):
    from urlparse import urlsplit
else:
    from urllib.parse import urlsplit
import collections

from pyownet import protocol

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
    parser.set_defaults(t_flags=protocol.FLG_TEMP_C)
    tempg = parser.add_mutually_exclusive_group()
    tempg.add_argument('-C', '--Celsius', const=protocol.FLG_TEMP_C,
                       help='Celsius(default) temperature scale',
                       dest='t_flags', action='store_const', )
    tempg.add_argument('-F', '--Fahrenheit', const=protocol.FLG_TEMP_F,
                       help='Fahrenheit temperature scale',
                       dest='t_flags', action='store_const', )
    tempg.add_argument('-K', '--Kelvin', const=protocol.FLG_TEMP_K,
                       help='Kelvin temperature scale',
                       dest='t_flags', action='store_const', )
    tempg.add_argument('-R', '--Rankine', const=protocol.FLG_TEMP_R,
                       help='Rankine temperature scale',
                       dest='t_flags', action='store_const', )

    # optional arg for address format
    fcodes = collections.OrderedDict((
        ('f.i', protocol.FLG_FORMAT_FDI),
        ('fi', protocol.FLG_FORMAT_FI),
        ('f.i.c', protocol.FLG_FORMAT_FDIDC),
        ('f.ic', protocol.FLG_FORMAT_FDIC),
        ('fi.c', protocol.FLG_FORMAT_FIDC),
        ('fic', protocol.FLG_FORMAT_FIC), ))
    parser.set_defaults(format='f.i')
    parser.add_argument('-f', '--format', choices=fcodes,
                        help='format for 1-wire unique serial IDs display')

    parser.add_argument('--nosys', '--only-sensors',
                        action='store_false', dest='bus',
                        help='do not descend system directories')
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
        parser.error(
            "Invalid URI '{}', no query component allowed".format(args.uri))
    host = urlc.hostname or 'localhost'
    port = urlc.port or 4304

    #
    # create owserver proxy object
    #
    try:
        proxy = protocol.proxy(
            host, port, flags=args.t_flags | fcodes[args.format],
            persistent=True)
    except (protocol.ConnError, protocol.ProtocolError) as error:
        parser.exit(status=1, message=str(error) + '\n')

    def walk(path):
        try:
            if not path.endswith('/'):
                val = proxy.read(path)
                print("{:40} {!r}".format(path, val))
            else:
                for entity in proxy.dir(path, bus=args.bus):
                    walk(entity)
        except protocol.OwnetError as error:
            print('Unable to walk {}: server says {}'.format(path, error),
                  file=sys.stderr)
        except protocol.ConnError as error:
            print('Unable to walk {}: {}'.format(path, error), file=sys.stderr)

    with proxy:
        walk(urlc.path)


if __name__ == '__main__':
    main()
