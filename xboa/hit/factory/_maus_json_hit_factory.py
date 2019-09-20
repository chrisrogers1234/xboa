
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

import sys
import json
import xboa.common as common
import xboa.hit
from xboa.hit.factory import HitFactoryBase

class MausJsonHitFactory(HitFactoryBase):
    """
    MausJsonHitFactory strips hits of a specified type from a json_document and
    returns to the user
    """
    def __init__(self, file_handle, format):
        """
        Initialise the hit factory
        - file_handle: a file handle containing a set of json documents, one per
                       line
        - format: format of data to be extracted from the json document
        - spill_number: spill parameter that will be assigned to the hits
        """
        if format in self.file_types():
            format = format[10:] # string maus_json_
        elif format in self.deprecated_file_types():
            print("Warning - using deprecated file type", format)
            format = format[5:] # strip maus_
        else:
            raise KeyError("Did not recognise format "+str(format))
        self.fin = file_handle
        self.hits = []
        self.format = format
        self.spill = None


    def new_spill(self):
        """
        Read a new spill off the file handle
        """
        # if we have no more hits, look for the next Spill event and attempt to
        # load MC
        found_spill = False
        if len(self.hits) == 0:
            while not found_spill:
                line = self.fin.readline()
                if line == "":
                    raise xboa.hit.BadEventError("Reached the end of the file")
                new_line = json.loads(line)
                if "maus_event_type" in new_line and \
                   new_line["maus_event_type"] == "Spill":
                    found_spill = True
                    self.spill = new_line
                    try:
                        self._read_maus_spill()
                    except KeyError:
                        pass # badly formed spill or no data

    def make_hit(self):
        """
        Return the next hit from the spill file_handle
        """
        # try to produce a new hit
        try:
            while len(self.hits) == 0:
                self.new_spill()
            hit = self.hits.pop(0)
            return hit
        except IndexError:
            raise xboa.hit.BadEventError("Run out of events")

    def _read_maus_spill(self):
        """
        Read a MAUS spill, converting to MAUS objects
        """
        if self.format == 'virtual_hit':
            self._read_virtual_hits()
        elif self.format == 'special_virtual_hit':
            self._read_special_virtual_hits()
        elif self.format == 'primary':
            self._read_primaries()

    def _read_virtual_hits(self):
        """
        Read a virtual hits from the json_document
        """
        for ev, mc_event in enumerate(self.spill["mc_events"]):
            for virtual_hit in mc_event["virtual_hits"]:
                hit = self.hit_from_maus_object("virtual_hit", virtual_hit, ev)
                hit["spill"] = self.spill["spill_number"]
                self.hits.append(hit)

    def _read_special_virtual_hits(self):
        """
        Read a virtual hits from the json_document
        """
        for ev, mc_event in enumerate(self.spill["mc_events"]):
            for virtual_hit in mc_event["special_virtual_hits"]:
                hit = self.hit_from_maus_object("special_virtual_hit", virtual_hit, ev)
                hit["spill"] = self.spill["spill_number"]
                self.hits.append(hit)

    def _read_primaries(self):
        """
        Read primaries from the json_document
        """
        for ev, mc_event in enumerate(self.spill["mc_events"]):
            hit = self.hit_from_maus_object("primary", mc_event["primary"], ev)
            hit["spill"] = self.spill["spill_number"]
            self.hits.append(hit)

    @classmethod
    def hit_from_maus_object(cls, format, maus_dict, event_number):
        """
        Convert a MAUS object into a Hit according to specified formats
        """
        xboa_dict = {}
        three_vec_conversions = cls._maus_three_vec_conversions[format]
        conversion_dict = cls._maus_variable_conversions[format]
        for maus_name, xboa_suffix in three_vec_conversions.iteritems():
          for maus_xyz, value in maus_dict[maus_name].iteritems():
            xboa_dict[xboa_suffix+maus_xyz] = value
        for maus_key, xboa_key in conversion_dict.iteritems():
          xboa_dict[xboa_key] = maus_dict[maus_key]
        xboa_dict['event_number'] = event_number
        if 'mass' not in xboa_dict.keys():
            try:
                xboa_dict['mass'] = common.pdg_pid_to_mass[abs(xboa_dict['pid'])]
            except KeyError:
                xboa_dict['mass'] = 0.
                cls.bad_pid(xboa_dict['pid'])
        if 'charge' not in xboa_dict.keys():
            try:
                xboa_dict['charge'] = common.pdg_pid_to_charge[xboa_dict['pid']]
            except KeyError:
                xboa_dict['charge'] = 0.
                cls.bad_pid(xboa_dict['pid'])
        hit = xboa.hit.Hit.new_from_dict(xboa_dict, cls._file_mass_shell[format])
        return hit


    @classmethod
    def file_types(cls):
        """Return a list of file types that the factory can read"""
        return ["maus_json_virtual_hit", "maus_json_primary", "maus_json_special_virtual_hit"]

    @classmethod
    def deprecated_file_types(cls):
        """Return a list of deprecated file types (no longer used)"""
        return ["maus_virtual_hit", "maus_primary"]

    _maus_three_vec_conversions = { # maus three vectors are sub-dicts of virtual_hit
      "virtual_hit":{"position":"", "momentum":"p", "b_field":"b", "e_field":"e"},
      "special_virtual_hit":{"position":"", "momentum":"p"},
      "primary":{"position":"", "momentum":"p"},
    }

    _maus_variable_conversions = {
      "virtual_hit":{"station_id":"station", "particle_id":"pid", "track_id":"particle_number", "time":"t", "mass":"mass", "charge":"charge", "proper_time":"proper_time", "path_length":"path_length"},
      "primary":{"particle_id":"pid", "time":"t", "energy":"energy"}, # we also force "mass" from "pid"
      "special_virtual_hit":{"particle_id":"pid", "track_id":"particle_number", "time":"t", "mass":"mass", "charge":"charge", "path_length":"path_length", "energy_deposited":"e_dep"},
    }


    _file_mass_shell = {
      "virtual_hit":"energy",
      "special_virtual_hit":"energy",
      "primary":"p"
    }

