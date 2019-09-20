
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
from xboa.hit.factory import LineFactoryBase

class UserHitFactory(LineFactoryBase):
    """
    Factory class for line by line reads of output files using a user-defined
    format
    """
    def __init__(self, format_list, format_units_dict, filehandle, mass_shell_condition):
        """
        Initialise the factory
        - format_list = ordered list of strings. Each string should be a valid
          Hit.set_variable()
        - format_units_dict = dict of formats mapping from format_list elements
          to units. Variables that are dimensionless or in natural units should
          have an empty string to denote natural units. If a variable is not
          listed at all, a KeyError will be raised
        - file_handle = file handle made using e.g. open() command
        - mass_shell_condition = string containing from Hit.mass_shell_variables
          that determines how the mass shell condition will be calculated (or
          set to '' to ignore)
        Returns a new factory class
        """
        super(LineFactoryBase, self).__init__()
        self.filehandle = filehandle
        self.format_list = format_list
        self.format_units_dict = format_units_dict
        for format in format_list:
            err_str = "Format key '"+str(format)+"' should be one of: "
            for var in xboa.hit.Hit.set_variables():
                err_str += var+", "
            if format not in xboa.hit.Hit.set_variables():
                raise KeyError(err_str)
            if xboa.hit.Hit._default_var_types[format] == float and format != '':
                if format not in self.format_units_dict:
                    raise KeyError("Missing unit for variable "+format)
                unit = self.format_units_dict[format]
                if unit not in common.units:
                    raise KeyError("Could not parse unit "+str(unit)+\
                                   " for variable "+str(format))
        self.mass_shell_condition = mass_shell_condition

    def make_hit(self):
        """
        Read the next line in the file handle and return a new hit object
        """
        hit = self._read_formatted(self.format_list,
                                   self.format_units_dict,
                                   self.filehandle,
                                   self.mass_shell_condition)
        if 'mass' not in self.format_list:
            hit.set('mass', common.pdg_pid_to_mass[abs(hit['pid'])])
        hit.mass_shell_condition(self.mass_shell_condition)
        if 'charge' not in self.format_list:
            hit.set('charge', common.pdg_pid_to_charge[hit['pid']])      
        return hit
