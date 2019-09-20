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
\namespace xboa::hit

Implemented within this module:
\li \link xboa::hit::_hit::Hit Hit \endlink: represents a particle at a point in
  phase space. Hit contains functions for i/o, as well as accessors for 
  rectangular or cylindrical coordinate systems and functions to perform
  translations, abelian transformations etc.
\li \link xboa::hit::factory factory \endlink: module containing hit "factory"
    classes that can be used for generating new hit objects, e.g. by reading in
    data from a file. These factory objects are wrapped by 
    \link xboa::bunch::_bunch::Bunch::new_from_read_builtin Bunch.new_from_read_builtin \endlink and this is the preferred way of loading data.
"""

from _hit import Hit
from _hit import BadEventError
all = ["Hit", "BadEventError"]


