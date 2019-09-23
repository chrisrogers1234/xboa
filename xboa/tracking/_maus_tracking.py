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
\namespace xboa::tracking::_maus_tracking

Should be imported directly from the xboa::tracking namespace
"""

import json
try:
    import maus_cpp.globals
    import maus_cpp.simulation
except ImportError:
    pass

from xboa import common
from xboa.common import config
from xboa.hit import Hit

from ._tracking_base import TrackingBase 

class MAUSTracking(TrackingBase):
    """
    Provides an interface to MAUS tracking routines for use by xboa.algorithms
    """
    def __init__(self, datacards=None, seed=0):
        """
        Ensure MAUS is initialised, ready for tracking
        - datacards json document containing datacards that will be used for
                    initialise MAUS. If datacards is None, TrackingMAUS will not
                    attempt to initialise MAUS and will not check that MAUS is
                    initialised.
        - seed initial random seed; each time a particle is fired, the seed
               increments by 1
        Raises an ImportError if maus is not installed or maus environment is
        not sourced
        """
        config.has_maus()
        TrackingBase.__init__(self)
        if type(datacards) == type({}) or type(datacards) == type([]):
           datacards = json.dumps(datacards)
        if datacards != None:
            if maus_cpp.globals.has_instance():
                maus_cpp.globals.death()
            maus_cpp.globals.birth(datacards)
        self.datacards = datacards
        self.random_seed = seed
        self.spill = 0
        self.last = []

    def track_one(self, hit):
        """
        Track a hit and return a list of output hits
        - hit initial Hit - particle to be tracked (of Hit type)

        Track a hit and return a list of output hits. The output hits should
        correspond to e.g. particle crossings over cell ends, depending on the
        usage of the Tracking object; see algorithm documentation.

        Spill number will increment by one for each call to track_one or
        track_many
        """
        return self.track_many([hit])[0]
        

    def track_many(self, list_of_hits):
        """
        Track many hits and return a list of list of output hits
        - list_of_hits list of Hits - initial particles to be tracked

        Track many hits and return a list containing a list of output hits,
        one for each track. This provides a hook for tracking codes that have
        significant set up and tear down times, or which simulate collective
        effects that need to be taken into account by the algorithm

        Spill number will increment by one for each call to track_one or
        track_many
        """
        primary_list = [self._hit_to_primary(hit) for hit in list_of_hits]
        primary_str = json.dumps(primary_list)
        mc_events_str = maus_cpp.simulation.track_particles(primary_str)
        mc_events = json.loads(mc_events_str)
        self.last = [self._mc_event_to_hit_list(event, i) \
                                           for i, event in enumerate(mc_events)]
        self.spill += 1
        return self.last

    def _mc_event_to_hit_list(self, mc_event, event_number):
        """
        Make a list of data from a MAUS mc event
        """
        hit_list = [self._primary_to_xboa_hit(mc_event["primary"],
                                              event_number, 1)]
        if "virtual_hits" in mc_event:
            hit_list += [self._virtual_hit_to_xboa_hit(vhit, event_number) \
                                           for vhit in mc_event["virtual_hits"]]
        return hit_list

    def _virtual_hit_to_xboa_hit(self, virtual_hit, event):
        """
        Fill hit data from a MAUS virtual hit
        - virtual_hit json object corresponding to the hit
        - event integer event number
        """
        hit = Hit()
        pid = virtual_hit["particle_id"]
        for key in 'x', 'y', 'z':
            hit[key] = virtual_hit['position'][key]
            hit["p"+key] = virtual_hit['momentum'][key]
        hit["pid"] = pid
        hit["t"] = virtual_hit["time"]
        hit["mass"] = common.pdg_pid_to_mass[abs(pid)]
        hit["charge"] = common.pdg_pid_to_charge[pid]
        hit["particle_number"] = virtual_hit["track_id"]
        hit["event_number"] = event
        hit["spill"] = self.spill
        hit["station"] = virtual_hit["station_id"]
        hit.mass_shell_condition("energy")
        return hit

    def _primary_to_xboa_hit(self, primary, event, particle):
        """
        Fill hit data from a MAUS primary
        """
        hit = Hit()
        pid = primary["particle_id"]
        for key in 'x', 'y', 'z':
            hit[key] = primary['position'][key]
            hit["p"+key] = primary['momentum'][key]
        hit["pid"] = pid
        hit["energy"] = primary["energy"]
        hit["t"] = primary["time"]
        hit["mass"] = common.pdg_pid_to_mass[abs(pid)]
        hit["charge"] = common.pdg_pid_to_charge[pid]
        hit["particle_number"] = particle
        hit["event_number"] = event
        hit["spill"] = self.spill
        hit["station"] = -1
        return hit

    def _hit_to_primary(self, hit):
        """
        Fill primary data from a hit
        """
        primary = {'primary':
          {
            'position':{'x':hit["x"], 'y':hit["y"], 'z':hit["z"]},
            'momentum':{'x':hit["px"], 'y':hit["py"], 'z':hit["pz"]},
            'particle_id':hit["pid"],
            'energy':hit["energy"],
            'time':hit["t"],
            'random_seed':self.random_seed
          }
        }
        self.random_seed += 1
        return primary

    def __getstate__(self):
        """
        """
        return {
            'datacards':self.datacards,
            'random_seed':self.random_seed,
            'spill':self.spill,
            'last':self.last
        }

    def __setstate__(self, state):
        """
        """
        datacards = state['datacards']
        random_seed = state['random_seed']
        self.__init__(datacards, random_seed)
        self.spill = state['spill']
        self.last = state['last']

