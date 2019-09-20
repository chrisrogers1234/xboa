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
from xboa.hit.factory import LineFactoryBase

class BuiltinHitFactory(LineFactoryBase):
    """
    Factory class for line by line reads of output files
    """
    def __init__(self, format, filehandle):
        super(LineFactoryBase, self).__init__()
        self.filehandle = filehandle
        self.format = str(format)
        if self.format not in self.file_formats.keys():
            raise KeyError("Did not recognise builtin format "+self.format+\
                     ". Should be one of "+str(self.file_formats.keys()))

    def make_hit(self):
        """
        Read a new hit from filehandle according to a predefined format
        - filehandle = file handle object
        Returns a new hit object
        """
        format = self.format
        hit = self._read_formatted(self.file_formats[format],
                                   self.file_units[format],
                                   self.filehandle, '')
        if(format.find('icool') > -1 ):
          hit.set('pid', common.icool_pid_to_pdg[hit.get('pid')])
        if( format.find('mars') > -1 ):
          hit.set('pid', common.mars_pid_to_pdg[hit.get('pid')])
        try:
          hit.set('mass', common.pdg_pid_to_mass[abs(hit.get('pid'))])
          hit.mass_shell_condition(self.file_mass_shell[format])
        except KeyError:
          hit.set('mass', 0.)
          hit.mass_shell_condition(self.file_mass_shell[format])
          if hit.get('pid') not in self.bad_pids:
            print('Warning - could not resolve PID ', hit.get('pid'), \
                  ' setting mass to 0.')
            self.bad_pids.append(hit.get('pid'))
        if 'charge' not in self.file_formats[format]:
          try:
            hit.set('charge', common.pdg_pid_to_charge[hit.get('pid')])
          except KeyError:
            if hit.get('pid') not in self.bad_pids:
              print('Warning - could not resolve PID ',hit.get('pid'),' setting charge to 0.')
              self.bad_pids.append(hit.get('pid'))
        return hit

    @classmethod
    def file_types(cls):
        return cls.file_formats

    #formatting information
    file_formats = {
      'icool_for009' : ['eventNumber', 'particleNumber', 'pid', 'status', 'station', 't', 'x', 'y', 'z', 'px', 'py', 'pz', 'bx', 'by', 'bz', 'local_weight', 
                           'ex', 'ey', 'ez', '', 'sx', 'sy', 'sz'],
      'icool_for003' : ['eventNumber', 'particleNumber', 'pid', 'status', 't', 'local_weight', 'x', 'y', 'z', 'px', 'py', 'pz', 'sx', 'sy', 'sz'],
      'g4beamline_bl_track_file'  : ['x','y','z','px','py','pz','t','pid','eventNumber','particleNumber', '','local_weight'],
      'mars_1'       : ['eventNumber','pid','x','y','z','px','py','pz','energy','ct','local_weight']
    }

    file_units = {
      'icool_for009' : {'eventNumber':'', 'particleNumber':'', 'pid':'', 'status':'', 'station':'', 't':'s', 'x':'m', 'y':'m', 'z':'m', 'px':'GeV/c', 'py':'GeV/c', 
      'pz':'GeV/c', 'bx':'T', 'by':'T', 'bz':'T', 'local_weight':'', 
                           'ex':'GV/m', 'ey':'GV/m', 'ez':'GV/m', 'sx':'', 'sy':'', 'sz':'', '':''},
      'icool_for003' : {'eventNumber':'', 'particleNumber':'', 'pid':'', 'status':'', 't':'s', 'local_weight':'', 'x':'m', 'y':'m', 'z':'m', 'px':'GeV/c', 'py':'GeV/c', 'pz':'GeV/c', 'sx':'', 'sy':'', 'sz':''},
      'g4beamline_bl_track_file'  : {'x':'mm','y':'mm','z':'mm','px':'MeV/c','py':'MeV/c','pz':'MeV/c','t':'ns','pid':'','eventNumber':'','station':'','local_weight':'', 'particleNumber':''},
      'mars_1'       : {'eventNumber':'','pid':'','x':'mm','y':'mm','z':'mm','px':'GeV/c','py':'GeV/c','pz':'GeV/c','energy':'GeV','ct':'cm','local_weight':''},
    }

    file_mass_shell     = {'icool_for009':'energy',
                           'icool_for003':'energy',
                           'g4beamline_bl_track_file':'energy', 
                           'mars_1':'energy'}


