"""python owserver client"""

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

__all__ = ['__version__', 'Error']
__version__ = '0.10.1.dev1+sensors7'


class Error(Exception):
    """Base class for all package errors"""

# map legacy classes to protocol module
from . import (protocol, legacy)
protocol.OwnetProxy = legacy.OwnetProxy
