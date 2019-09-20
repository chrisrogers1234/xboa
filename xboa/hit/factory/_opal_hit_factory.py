
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

from xboa.hit.factory import LineFactoryBase

class OpalHitFactory(LineFactoryBase):
    """
    Factory class for line by line reads of OPAL output files
    """
    def __init__(self, pid, probes, ignore_probes, filehandle):
        super(LineFactoryBase.__init__(self))
        if pid not in Common.pdg_pid_to_mass or \
           pid not in Common.pdg_pid_to_charge:
            raise
        self.pid = pid
        self.probes = probes
        self.ignore_probes = []
        self.filehandle = filehandle

    # read beam loss hit
    # probes is the list of probes discovered - appended to dynamically
    def make_hit(self):
        """
        Read a new hit from filehandle
        - filehandle = file handle object
        Returns a new hit object

        Raises an EOFError if end of file is hit
        """
        probes = self.probes
        pid = self.pid
        try:
          line = self.filehandle.next()
        except StopIteration:
          raise EOFError("End of file reached")
        words = line.split()
        if words[0] in self.ignore_probes:
          raise BadEventError("Failed to parse event")
        if not len(words) == 10:
          raise BadEventError("Failed to parse event")
        if words[0] not in probes.keys():
          probes[words[0]] = len(probes.keys())
        hit_dict = dict( (key, float(words[i+1]) ) for i, key in enumerate(['x', 'y', 'z', 'px', 'py', 'pz', 'event_number', 'station', 't']))
        hit_dict['pid'] = pid
        hit_dict['mass'] = Common.pdg_pid_to_mass[abs(pid)]
        hit_dict['charge'] = Common.pdg_pid_to_charge[pid]
        hit_dict['station'] = probes[words[0]]+len(probes)*(int(words[8])-1)
        for item in ['px', 'py', 'pz']:
          hit_dict[item] *= hit_dict['mass']
        hit = Hit.new_from_dict(hit_dict)
        hit.mass_shell_condition('energy')
        return hit

