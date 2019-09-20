
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

import json
import ROOT
import xboa.common as common
import xboa.hit.factory
from xboa.hit.factory import HitFactoryBase

class MausRootHitFactory(HitFactoryBase):
    """
    MausRootHitFactory reads hits of a specified type from a root spill
    """
    def __init__(self, root_tree, format, entry = 0, test_function = None):
        """
        Initialise the hit factory
        - root_tree: a object of type ROOT.TTree that should contain a branch
                called "Data" containing a list of MAUS.ROOT.TTrees
        - format: format of data to be extracted from the ROOT document
        - entry: entry that will be read to get the ROOT data
        - test_function: if not None, only return hits for which 
          test_function(hit) == True
        """
        if format not in self.file_types():
            raise KeyError("Did not recognise format "+str(format))
        self.entry = entry
        self.hits = []
        self.format = format[10:] # strip maus_root_
        self.tree = root_tree
        self.spill = None
        self.test_function = test_function

    def new_spill(self):
        data = ROOT.MAUS.Data()
        self.tree.SetBranchAddress("data", data)
        if self.entry >= self.tree.GetEntries():
            raise IndexError("Out of entries")
        self.tree.GetEntry(self.entry)
        self.spill = data.GetSpill()
        self.spill_number = self.spill.GetSpillNumber()
        self._read_maus_spill()
        self.hits = [hit for hit in self.hits \
                       if self.test_function == None or self.test_function(hit)]
        self.entry += 1

    def make_hit(self):
        """
        Return the next hit from the given spill document
        """
        try:
            while len(self.hits) == 0:
                self.new_spill()
            return self.hits.pop(0)
        except IndexError:
            raise xboa.hit.BadEventError("Run out of events")

    def _read_maus_spill(self):
        """
        Read a MAUS spill, converting to MAUS objects
        """
        if self.format == 'virtual_hit':
            self._read_virtual_hits()
        elif self.format == 'primary':
            self._read_primaries()
        elif self.format == 'step':
            self._read_steps()

    def _read_virtual_hits(self):        
        """
        Read virtuals from the Spill
        """
        for event, mc_event in enumerate(self.spill.GetMCEvents()):
            for virtual_hit in mc_event.GetVirtualHits():
                hit = xboa.hit.Hit()
                hit["x"] = virtual_hit.GetPosition().x()
                hit["y"] = virtual_hit.GetPosition().y()
                hit["z"] = virtual_hit.GetPosition().z()
                hit["px"] = virtual_hit.GetMomentum().x()
                hit["py"] = virtual_hit.GetMomentum().y()
                hit["pz"] = virtual_hit.GetMomentum().z()
                hit["bx"] = virtual_hit.GetBField().x()
                hit["by"] = virtual_hit.GetBField().y()
                hit["bz"] = virtual_hit.GetBField().z()
                hit["ex"] = virtual_hit.GetEField().x()
                hit["ey"] = virtual_hit.GetEField().y()
                hit["ez"] = virtual_hit.GetEField().z()
                hit["pid"] = virtual_hit.GetParticleId()
                hit["station"] = virtual_hit.GetStationId()
                hit["particle_number"] = virtual_hit.GetTrackId()
                hit["t"] = virtual_hit.GetTime()
                hit["mass"] = virtual_hit.GetMass()
                hit["charge"] = virtual_hit.GetCharge()
                hit["proper_time"] = virtual_hit.GetProperTime()
                hit["path_length"] = virtual_hit.GetPathLength()
                hit["spill"] = self.spill_number
                hit["event_number"] = event
                hit.mass_shell_condition('energy')
                self.hits.append(hit)

    def _read_steps(self):        
        """
        Read steps from the Spill
        """
        for event, mc_event in enumerate(self.spill.GetMCEvents()):
            for track_index, track in enumerate(mc_event.GetTracks()):
                for step_index, step in enumerate(track.GetSteps()):
                    hit = xboa.hit.Hit()
                    hit["x"] = step.GetPosition().x()
                    hit["y"] = step.GetPosition().y()
                    hit["z"] = step.GetPosition().z()
                    hit["t"] = step.GetTime()
                    hit["px"] = step.GetMomentum().x()
                    hit["py"] = step.GetMomentum().y()
                    hit["pz"] = step.GetMomentum().z()
                    hit["bx"] = step.GetBField().x()
                    hit["by"] = step.GetBField().y()
                    hit["bz"] = step.GetBField().z()
                    hit["ex"] = step.GetEField().x()
                    hit["ey"] = step.GetEField().y()
                    hit["ez"] = step.GetEField().z()
                    hit["sx"] = step.GetSpin().x()
                    hit["sy"] = step.GetSpin().y()
                    hit["sz"] = step.GetSpin().z()
                    hit["station"] = step_index
                    hit["pid"] = track.GetParticleId()
                    hit["particle_number"] = track.GetTrackId()
                    hit["mass"] = common.pdg_pid_to_mass[abs(hit["pid"])]
                    hit["charge"] = common.pdg_pid_to_charge[hit["pid"]]
                    hit["proper_time"] = step.GetProperTime()
                    hit["path_length"] = step.GetPathLength()
                    hit["spill"] = self.spill_number
                    hit["event_number"] = event
                    hit.mass_shell_condition('energy')
                    self.hits.append(hit)

    def _read_primaries(self):
        """
        Read primaries from the Spill
        """
        for event, mc_event in enumerate(self.spill.GetMCEvents()):
            hit = xboa.hit.Hit()
            primary = mc_event.GetPrimary()
            hit["x"] = primary.GetPosition().x()
            hit["y"] = primary.GetPosition().y()
            hit["z"] = primary.GetPosition().z()
            hit["px"] = primary.GetMomentum().x()
            hit["py"] = primary.GetMomentum().y()
            hit["pz"] = primary.GetMomentum().z()
            hit["pid"] = primary.GetParticleId()
            hit["energy"] = primary.GetEnergy()
            hit["spill"] = self.spill_number
            hit["event_number"] = event
            hit["t"] = primary.GetTime()
            try:
                hit["mass"] = common.pdg_pid_to_mass[abs(hit["pid"])]
            except KeyError:
                hit["mass"] = 0.
                self.bad_pid(hit["pid"])
            try:
                hit["charge"] = common.pdg_pid_to_charge[hit["charge"]]
            except KeyError:
                hit["charge"] = 0.
                self.bad_pid(hit["pid"])
            hit.mass_shell_condition('p')
            self.hits.append(hit)
 
    @classmethod
    def file_types(cls):
        """
        List of file types that can be read by this class
        """
        return ["maus_root_virtual_hit",
                "maus_root_primary",
                "maus_root_step",
              ]

    sf_tracker_coeff = 100    
    sf_station_coeff = 10    
    sf_plane_coeff = 1    
    sf_station_offset = 90000

