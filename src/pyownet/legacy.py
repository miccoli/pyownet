"""legacy classes limbo

classes and code in this module will go away, soon or later
"""

#
# Copyright 2013-2016 Stefano Miccoli
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

import warnings
import socket
from .protocol import (_Proxy, _errtuple, FLG_OWNET, PTH_ERRCODES,
                       ConnError, OwnetError, bytes2str)

__all__ = ['OwnetProxy', ]


#
# class OwnetProxy is deprecated and for legacy support only,
# please use factory function protocol.proxy
#

class OwnetProxy(_Proxy):
    """This class is for legacy support only, and is deprecated."""

    def __init__(self, host='localhost', port=4304, flags=0,
                 verbose=False, ):
        """return an owserver proxy object bound at (host, port); default is
        (localhost, 4304).

        'flags' are or-ed in the header of each query sent to owserver.
        If verbose is True, details on each sent and received packet is
        printed on stdout.
        """

        # this class is deprecated since version 0.9.0
        warnings.warn(DeprecationWarning("Please use factory functions"))

        # save init args
        self.flags = flags | FLG_OWNET
        self.verbose = verbose

        # default (empty) errcodes tuple
        self.errmess = _errtuple()

        #
        # init logic:
        # try to connect to the given owserver, send a MSG_NOP,
        # and check answer
        #

        # resolve host name/port
        try:
            gai = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
        except socket.gaierror as err:
            raise ConnError(*err.args)

        # gai is a list of tuples, search for the first working one
        lasterr = None
        for (self._family, _, _, _, self._sockaddr) in gai:
            try:
                self.ping()
            except ConnError as err:
                # not working, go over to next sockaddr
                lasterr = err
            else:
                # ok, this is working, stop searching
                break
        else:
            # no working (sockaddr, family) found: reraise last exception
            assert isinstance(lasterr, ConnError)
            raise lasterr

        # fetch errcodes array from owserver
        try:
            self.errmess = _errtuple(
                m for m in bytes2str(self.read(PTH_ERRCODES)).split(','))
        except OwnetError:
            # failed, leave the default empty errcodes defined above
            pass
