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
tests of tracking_maus
"""

import os 
import sys 
import json
import unittest

from xboa.hit import Hit
import xboa.common as Common
import Configuration
from xboa.tracking import MAUSTracking

class TestMAUSTracking(unittest.TestCase):
    """
    Test that we can correctly interface to MAUS
    """
    def setUp(self):
        """
        Generate test config
        """
        _config = Configuration.Configuration().getConfigJSON()
        self.config = json.loads(_config)
        self.config["simulation_geometry_filename"] = os.path.join(
            '/', sys.prefix, 'share' ,'xboa', 'data', 'test_config.dat'
        )

    def test_tracking_init(self):
        """
        Test MAUSTracking.__init__
        """
        tracking = MAUSTracking()
        try:
            tracking = MAUSTracking(1)
            self.assertTrue(False, msg="Should have raised")
        except TypeError:
            pass
        try:
            tracking = MAUSTracking("")
            self.assertTrue(False, msg="Should have raised")
        except RuntimeError:
            pass
        config = Configuration.Configuration().getConfigJSON()
        tracking = MAUSTracking(config)
        config = json.loads(config)
        tracking = MAUSTracking(config)
        tracking = MAUSTracking(config, 22)
        self.assertEqual(tracking.random_seed, 22)
        self.assertEqual(tracking.last, [])

    def test_track_one(self):
        """
        Test MAUSTracking.track_one
        """
        # BUG: G4 does not reinitialise properly if run after test_tracking_init
        tracking = MAUSTracking(self.config, 99)
        hit_in = Hit.new_from_dict({"mass":Common.pdg_pid_to_mass[2212],
                                    "charge":1.,
                                    "energy": 10000., "pid":2212, "pz":1.},
                                    "pz")
        hit_list = tracking.track_one(hit_in)
        self.assertEqual(len(hit_list), 6)
        for i, hit_out in enumerate(hit_list):
            for key in ["pid", "mass", "charge",
                        "x", "y", "energy", "px", "py", "pz"]:
                mess = "Failed on "+key+" "+\
                       str(hit_in[key])+", "+str(hit_out[key])
                self.assertAlmostEqual(hit_in[key], hit_out[key], 3, msg=mess)
            self.assertEqual(hit_out["z"], i*1000.)
            self.assertEqual(hit_out["event_number"], 0)
            self.assertEqual(hit_out["particle_number"], 1)
            self.assertEqual(hit_out["spill"], 0)
        hit_list = tracking.track_one(hit_in)
        self.assertEqual(len(hit_list), 6)
        for i, hit_out in enumerate(hit_list):
            self.assertEqual(hit_out["event_number"], 0)
            self.assertEqual(hit_out["particle_number"], 1)
            self.assertEqual(hit_out["spill"], 1)
        self.assertEqual(tracking.last, [hit_list])

    def test_track_many(self):
        """
        Test MAUSTracking.track_many
        """
        tracking = MAUSTracking(self.config)
        hit_in = Hit.new_from_dict({"mass":Common.pdg_pid_to_mass[13],
                                    "charge":1.,
                                    "energy": 226., "pid":-13, "pz":200.},
                                    "energy")
        hit_list_of_lists = tracking.track_many([hit_in]*5)
        self.assertEqual(len(hit_list_of_lists), 5)
        for i, hit_list in enumerate(hit_list_of_lists):
            for j, hit_out in enumerate(hit_list):
                for key in ["pid", "mass", "charge",
                            "x", "y", "energy", "px", "py", "pz"]:
                    mess = "Failed on "+key+" "+\
                           str(hit_in[key])+", "+str(hit_out[key])
                    self.assertAlmostEqual(hit_in[key], hit_out[key], 3,
                                           msg=mess)
                self.assertEqual(hit_out["z"], j*1000.)
                self.assertEqual(hit_out["event_number"], i)
                self.assertEqual(hit_out["particle_number"], 1)
                self.assertEqual(hit_out["spill"], 0)
        self.assertEqual(tracking.last, hit_list_of_lists)
        

if __name__ == "__main__":
    unittest.main()



