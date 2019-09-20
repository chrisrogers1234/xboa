#This file is a part of xboa
#
#xboa is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#xboa is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with xboa in the doc folder.  If not, see 
#<http://www.gnu.org/licenses/>.

"""
\namespace xboa::bunch

Implemented within this module:
\li \link xboa::bunch::_bunch::Bunch Bunch \endlink: the Bunch object is a 
collection of Hits that can be taken together to make up a bunch
\li \link xboa::bunch::weighting weighting \endlink: module containing
    statistical weighting routines that can apply to Bunch objects.
"""

from ._bunch import Bunch
__all__ = ["Bunch"]

