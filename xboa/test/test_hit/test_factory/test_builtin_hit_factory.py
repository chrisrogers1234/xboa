import os
import unittest

import xboa.Common as common
from xboa.hit import Hit
from xboa.hit.factory import BuiltinHitFactory

def tmp_name():
    tmp = os.path.expandvars("/tmp/test_io_builtin_formatted_test")
    if os.getenv("TMPDIR"):
        tmp = os.path.expandvars("$TMPDIR/test_io_builtin_formatted_test")
    return tmp

class UserHitFactoryTestCase(unittest.TestCase):
    def test_init(self):
        filehandle = open(tmp_name(), 'w')
        try:
            BuiltinHitFactory("not_a_format", filehandle)
            self.assertTrue(False, msg="Should have thrown")
        except KeyError:
            pass
        # no type checking on the filehandle object
        BuiltinHitFactory("icool_for003", "not a filehandle")
        # but this works okay
        fac = BuiltinHitFactory("icool_for003", filehandle)
        self.assertEqual(fac.format, "icool_for003")
        self.assertEqual(fac.filehandle, filehandle)

    def test_make_hit(self):
        ref_hit = Hit.new_from_dict({
            'x':1.,
            'y':2.,
            'z':3.,
            't':4.,
            'px':5.,
            'py':6.,
            'pz':7.,
            'pid':13,
            'mass':common.pdg_pid_to_mass[13],
            'charge':-1,
            'station':8,
            'event_number':9,
            'particle_number':10,
            'spill':0},
            'energy'
        )
        for format in BuiltinHitFactory.file_types():
            filehandle = open(tmp_name(), 'w')
            if not filehandle:
                raise unittest.SkipTest("Failed to open filehandle")
            ref_hit.write_builtin_formatted(format, filehandle)
            filehandle.close()
            
            filehandle = open(tmp_name(), 'r')
            fac = BuiltinHitFactory(format, filehandle)
            test_hit = fac.make_hit()
            skips = {
              'station':['icool_for003', 'mars_1', 'g4beamline_bl_track_file'],
              'particle_number':['g4beamline_bl_track_file', 'mars_1'],
            }
            for var, format_list in skips.iteritems(): 
                if format in format_list:
                    test_hit[var] = ref_hit[var]
            self.assertEqual(test_hit, ref_hit)
            filehandle.close()

if __name__ == "__main__":
    unittest.main()

