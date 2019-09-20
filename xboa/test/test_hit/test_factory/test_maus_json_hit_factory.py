import xboa.Common as common
from xboa.hit import BadEventError
from xboa.hit.factory import MausJsonHitFactory
import unittest
import json
import StringIO

def _json(obj_1, obj_2 = None, obj_3 = None):
    a_string = json.dumps(obj_1)
    if obj_2 != None:
        a_string += "\n"+json.dumps(obj_2)
    if obj_3 != None:
        a_string += "\n"+json.dumps(obj_3)
    return StringIO.StringIO(a_string)

class TestMausJsonHitFactory(unittest.TestCase):
    def test_init_no_hits(self):
        try: # empty document - no spill structure at all
            fac = MausJsonHitFactory(StringIO.StringIO(""), "maus_json_primary")
            fac.make_hit()
            self.assertTrue(False)
        except BadEventError:
            pass
        try: # empty document - run out of events
            fac = MausJsonHitFactory(_json({"maus_event_type":"Spill",
                                            "mc_events":[]}),
                                     "maus_json_primary")
            fac.make_hit()
            self.assertTrue(False)
        except BadEventError:
            pass

    def test_init_bad_format(self):
        try:
            fac = MausJsonHitFactory({"mc_events":[]}, "maus_none")
            self.assertTrue(False)
        except KeyError:
            pass

    def test_init_bad_pid(self):
        # note deprecated file type here
        pid = int(1e10)
        MausJsonHitFactory.bad_pids = []
        fac = MausJsonHitFactory(_json({"mc_events":[{"primary":{
                "position":{"x":1., "y":2., "z":3.},
                "momentum":{"x":4., "y":5., "z":6.},
                "energy":200., "particle_id":pid, "random_seed":1, "time":7.
            }
        }]*4, "spill_number":99, "maus_event_type":"Spill"}), "maus_primary")
        fac.make_hit()
        fac.make_hit()
        self.assertEqual(fac.bad_pids, [pid])
        fac.bad_pids = []

    def test_init_multi(self):
        # should ignore first 2 lines
        fac = MausJsonHitFactory(_json(
            [],
            {"maus_event_type":"bob"},
            {"mc_events":[{"primary":{
                "position":{"x":1., "y":2., "z":3.},
                "momentum":{"x":4., "y":5., "z":6.},
                "energy":200., "particle_id":13, "random_seed":1, "time":7.
            }}]*3, "spill_number":99, "maus_event_type":"Spill"}),
            "maus_json_primary")
        hit = fac.make_hit()
        self.assertEqual(hit["pid"], 13)

    def test_init_primary(self):
        fac = MausJsonHitFactory(_json({"mc_events":[{"primary":{
                "position":{"x":1., "y":2., "z":3.},
                "momentum":{"x":4., "y":5., "z":6.},
                "energy":200., "particle_id":13, "random_seed":1, "time":7.
            }
        }]*3, "spill_number":99, "maus_event_type":"Spill"}), "maus_json_primary")
        hit = fac.make_hit()
        self.assertAlmostEqual(hit["x"], 1.)
        self.assertAlmostEqual(hit["y"], 2.)
        self.assertAlmostEqual(hit["z"], 3.)
        self.assertAlmostEqual(hit["px"]/hit["pz"], 4./6.)
        self.assertAlmostEqual(hit["py"]/hit["pz"], 5./6.)
        self.assertAlmostEqual(hit["energy"], 200.)
        self.assertAlmostEqual(hit["pid"], 13)
        self.assertAlmostEqual(hit["t"], 7.)
        self.assertAlmostEqual(hit["spill"], 99)
        self.assertEqual(hit["event_number"], 0)
        hit = fac.make_hit()
        self.assertEqual(hit["event_number"], 1)
        hit = fac.make_hit()
        self.assertEqual(hit["event_number"], 2)
        try:
            hit = fac.make_hit()
            self.assertTrue(False, msg="Should have thrown")
        except BadEventError:
            pass

    def test_init_virtual_hit(self):
        fac = MausJsonHitFactory(_json({"mc_events":[{"virtual_hits":[{
                "position":{"x":1., "y":2., "z":3.},
                "momentum":{"x":4., "y":5., "z":6.},
                "b_field":{"x":14., "y":15., "z":16.},
                "e_field":{"x":17., "y":18., "z":19.},
                "station_id":8, "particle_id":13, "track_id":9, "time":10.,
                "mass":common.pdg_pid_to_mass[13], "charge":1.,
                "proper_time":11., "path_length":12.,
            }]*2
        }]*3, "spill_number":99, "maus_event_type":"Spill"}), "maus_json_virtual_hit")
        hit = fac.make_hit()
        test = {"x":1., "y":2., "z":3., "px":4., "py":5., "pz":6., "t":10.,
        "bx":14., "by":15., "bz":16., "ex":17., "ey":18., "ez":19.,
        "pid":13, "station":8, "pid":13, "particle_number":9., "spill":99,
        "charge":1., "proper_time":11., "path_length":12., "event_number":0}
        for key, var in test.iteritems():
            self.assertAlmostEqual(hit[key], var)
        hit = fac.make_hit()
        self.assertEqual(hit["event_number"], 0)
        hit = fac.make_hit()
        hit = fac.make_hit()
        self.assertEqual(hit["event_number"], 1)
        hit = fac.make_hit()
        hit = fac.make_hit()
        self.assertEqual(hit["event_number"], 2)
        try:
            hit = fac.make_hit()
            self.assertTrue(False, msg="Should have thrown")
        except BadEventError:
            pass

if __name__ == "__main__":
    unittest.main()

