
# This file is a part of xboa
#
# xboa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xboa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xboa in the doc folder.  If not, see 
# <http://www.gnu.org/licenses/>.

import xboa.common as common
import xboa.hit
from xboa.hit.factory import HitFactoryBase

class LineFactoryBase(HitFactoryBase):
    """
    Base factory class for line by line reads

    LineFactoryBase defines the interface for line-by-line IO of a text file to
    make hits. LineFactoryBase is a factory class i.e. it is used for generating
    new hits from a file
    """
    def __init__(self):
        """
        Initialise the base class
        """
        super(LineFactoryBase, self).__init__()

    def make_hit(self):
        """
        Read a new hit
        """
        raise NotImplementedError("read_hit not implemented")

    @classmethod
    def _read_formatted(cls, format_list, format_units_dict, file_handle, mass_shell_condition):
        """
        Read a line and parse according to some pre-defined format
        """
        try:
            line = next(file_handle)
        except StopIteration:
            raise EOFError("End of file reached")
        words = line.split()
        words.reverse()
        if not(len(words) == len(format_list)): 
            raise xboa.hit.BadEventError("Read operation failed with line "+str(line))
        a_hit = xboa.hit.Hit()
        for key in format_list:
            value = words.pop()
            if key != '':
                try:
                    value = xboa.hit.Hit._default_var_types[key](value)
                # I ran into problems with int > 1000000 written in scientific 
                # notation by G4BL (urk)
                except ValueError:
                    value = float(value)
                    value = xboa.hit.Hit._default_var_types[key](value)
                if xboa.hit.Hit._default_var_types[key] == float:
                    value *= common.units[format_units_dict[key]]
                a_hit.set(key, value)
        return a_hit

