
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

class MausRootReconHitFactory(HitFactoryBase):
    """
    MausReconHitFactory reads hits of a specified type from a root spill
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
        Read a maus spill
        """
        for rec_i, recon_event in enumerate(self.spill.GetReconEvents()):
            scifi_event = recon_event.GetSciFiEvent()
            scifi_trackpoints = [hit for hit in self._read_scifi_trackpoints(scifi_event)]
            if len(scifi_trackpoints) == 0:
                continue
            for trackpoint in scifi_trackpoints:
                trackpoint["event_number"] = rec_i
            if self.format == "scifi_trackpoint":
                self.hits += scifi_trackpoints
                continue
            tof_event = recon_event.GetTOFEvent()
            delta_t = self._read_tof_01_space_points(tof_event)
            if len(delta_t) == 0 and self.fallback_on_slabs:
                delta_t = self._read_tof_01_slab_hits(tof_event)
            if len(delta_t) == 0 and self.fallback_on_digits:
                delta_t = self._read_tof_01_digits(tof_event)
            print
            if len(delta_t) == 0:
                continue
            for trackpoint in scifi_trackpoints:
                trackpoint["t"] = delta_t[0]
            self.hits += scifi_trackpoints

    def _read_scifi_trackpoints(self, scifi_event):
        """
        Read scifitracks from the recon_event
        """
        for track_i, track in enumerate(scifi_event.scifitracks()):
            if self.sf_p_value_cut > 0. and \
               track.P_value() < self.sf_p_value_cut:
                continue
            for trackpoint in track.scifitrackpoints():
                sf_tracker = trackpoint.tracker()
                sf_station = trackpoint.station()
                sf_plane = trackpoint.plane()
                if sf_tracker > 10 or sf_tracker < 0 or \
                   sf_station > 10 or sf_station < 0 or \
                   sf_plane > 10 or sf_plane < 0:
                    raise ValueError("scifi trackpoint station index out of range")
                station = self.sf_station_offset+\
                          sf_tracker*self.sf_tracker_coeff+\
                          sf_station*self.sf_station_coeff+\
                          sf_plane*self.sf_plane_coeff
                hit = xboa.hit.Hit()
                hit["station"] = station
                hit["x"] = trackpoint.pos().x()
                hit["y"] = trackpoint.pos().y()
                hit["z"] = trackpoint.pos().z()
                hit["px"] = trackpoint.mom().x()
                hit["py"] = trackpoint.mom().y()
                hit["pz"] = trackpoint.mom().z()
                hit["spill"] = self.spill_number
                hit["particle_number"] = track_i
                yield hit
        raise StopIteration("Out of events")

    def _read_tof_01_space_points(self, tof_event):
        """
        Read TOF between tof 0 and tof 1
        """
        space_points = tof_event.GetTOFEventSpacePoint()
        tof0_list = [t.GetTime() for t in space_points.GetTOF0SpacePointArray()]
        tof1_list = [t.GetTime() for t in space_points.GetTOF1SpacePointArray()]
        print "number of tof0 sps:", len(tof0_list), "number of tof1_sps:", len(tof1_list), 
        tof01_list = []
        for tof1 in tof1_list:
            for tof0 in tof0_list:
                tof01_list.append(tof1-tof0)
        return tof01_list

    def _read_tof_01_slab_hits(self, tof_event):
        slab_hits = tof_event.GetTOFEventSlabHit()
        tof0_slabs = [hit.GetRawTime() for hit in slab_hits.GetTOF0SlabHitArray()]
        tof1_slabs = [hit.GetRawTime() for hit in slab_hits.GetTOF1SlabHitArray()]
        print "number of tof0 slabs:", len(tof0_slabs), "number of tof1 slabs:", len(tof1_slabs), 
        if len(tof0_slabs) > 0 and len(tof1_slabs) > 0:
            tof0_mean = sum(tof0_slabs)/len(tof0_slabs)
            tof1_mean = sum(tof1_slabs)/len(tof1_slabs)
            return [tof1_mean-tof0_mean]
        return []

    def _read_tof_01_digits(self, tof_event):
        digits = tof_event.GetTOFEventDigit()
        tof0_digs = [dig.GetLeadingTime() for dig in digits.GetTOF0DigitArray()]
        tof1_digs = [dig.GetLeadingTime() for dig in digits.GetTOF1DigitArray()]
        print "number of tof0 digs:", len(tof0_digs), "number of tof1 digs:", len(tof1_digs), 
        if len(tof0_digs) > 0 and len(tof1_digs) > 0:
            tof0_mean = sum(tof0_digs)/len(tof0_digs)
            tof1_mean = sum(tof1_digs)/len(tof1_digs)
            return [tof1_mean-tof0_mean]
        return []

    @classmethod
    def file_types(cls):
        """
        List of file types that can be read by this class
        """
        return ["maus_root_scifi_trackpoint", "maus_root_scifi_and_tof"]

    _file_mass_shell = {
      "virtual_hit":"energy",
      "primary":"p"
    }

    sf_tracker_coeff = 100    
    sf_station_coeff = 10    
    sf_plane_coeff = 1    
    sf_station_offset = 90000
    sf_p_value_cut = -1.

    fallback_on_slabs = True
    fallback_on_digits = True


