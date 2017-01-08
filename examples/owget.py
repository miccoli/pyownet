"""owget.py -- a pyownet implementation of owget

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

import sys
import argparse
if sys.version_info < (3, ):
    from urlparse import urlsplit
else:
    from urllib.parse import urlsplit
import collections
from binascii import hexlify

from pyownet import protocol

__all__ = ['main']


def main():
    """parse commandline arguments and print result"""

    fcodes = collections.OrderedDict((
        ('f.i', protocol.FLG_FORMAT_FDI),
        ('fi', protocol.FLG_FORMAT_FI),
        ('f.i.c', protocol.FLG_FORMAT_FDIDC),
        ('f.ic', protocol.FLG_FORMAT_FDIC),
        ('fi.c', protocol.FLG_FORMAT_FIDC),
        ('fic', protocol.FLG_FORMAT_FIC), ))

    def make_parser():
        # command line parsing

        parser = argparse.ArgumentParser()

        # positional args
        parser.add_argument('uri', metavar='URI', nargs='?', default='/',
                            help='[owserver:]//hostname:port/path')

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
        parser.set_defaults(format='f.i')
        parser.add_argument('-f', '--format', choices=fcodes,
                            help='format for 1-wire unique serial IDs display')

        # optional arg for output format
        tempg = parser.add_mutually_exclusive_group()
        tempg.add_argument('--hex', action='store_true',
                           help='write data in hex format')
        tempg.add_argument('-b', '--binary', action='store_true',
                           help='output binary data')

        # debug output
        parser.add_argument('-d', '--debug', action='store_true',
                            help='debug output')

        return parser

    def print_data(data):
        # format and print data

        if args.binary:
            if sys.version_info < (3, ):
                sys.stdout.write(data)
            else:
                sys.stdout.buffer.write(data)
        else:
            if args.hex:
                data = hexlify(data)
            else:
                try:
                    data = data.decode('ascii')
                except UnicodeDecodeError:
                    data = repr(data)
            print(data)

    #
    # main program starts here
    #

    #
    # parse command line arguments
    #
    parser = make_parser()
    args = parser.parse_args()

    #
    # parse args.uri and substitute defaults
    #
    urlc = urlsplit(args.uri, scheme='owserver', allow_fragments=False)
    assert urlc.fragment == ''
    if urlc.scheme != 'owserver':
        parser.error("Invalid URI scheme '{0}:'".format(urlc.scheme))
    if urlc.query:
        parser.error("Invalid URI, query component '?{0}' not allowed"
                     .format(urlc.query))
    try:
        host = urlc.hostname or 'localhost'
        port = urlc.port or 4304
    except ValueError as error:
        parser.error("Invalid URI: invalid net location '//{0}/'"
                     .format(urlc.netloc))

    #
    # create owserver proxy object
    #
    try:
        owproxy = protocol.proxy(
            host, port, flags=args.t_flags | fcodes[args.format],
            verbose=args.debug, )
    except protocol.ConnError as error:
        print("Unable to open connection to '{0}:{1}'\nSystem error: {2}"
              .format(host, port, error), file=sys.stderr)
        sys.exit(1)
    except protocol.ProtocolError as error:
        print("'{0}:{1}' not an owserver?\nProtocol error: {2}"
              .format(host, port, error), file=sys.stderr)
        sys.exit(1)

    #
    # query owserver and print results
    #
    try:
        if urlc.path.endswith('/'):
            for path in owproxy.dir(urlc.path, bus=True):
                print(path)
        else:
            data = owproxy.read(urlc.path)
            print_data(data)
    except protocol.OwnetError as error:
        print("Remote server error: {2}"
              .format(host, port, error), file=sys.stderr)
        sys.exit(1)
    except protocol.ProtocolError as error:
        print("'{0}:{1}' buggy?\nProtocol error: {2}"
              .format(host, port, error), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
