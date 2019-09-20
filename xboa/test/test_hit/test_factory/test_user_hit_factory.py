import os
import unittest

from xboa.hit import Hit
import xboa.Common as common
from xboa.hit.factory import UserHitFactory

def tmp_name():
    tmp = os.path.expandvars("/tmp/test_io_user_formatted_test")
    if os.getenv("TMPDIR"):
        tmp = os.path.expandvars("$TMPDIR/test_io_user_formatted_test")
    return tmp

class UserHitFactoryTestCase(unittest.TestCase):
    def test_make_hit(self):
        format_list = ['', 'x', 'y', 'z', 'energy', 'pid']
        format_units_dict = {'x':'mm', 'y':'m', 'z':'cm', 'energy':'', 'pz':'',
                             'pid':''}
        filehandle = open(tmp_name(), 'w')
        if not filehandle:
            raise unittest.SkipTest("Failed to open filehandle")
        filehandle.write('-99. 1. 2. 3. 4. -13\n')
        filehandle.write('-99. 1. 2. 3. 4. -13\n')
        filehandle.write('-99. 1. 2. 3. 4.')
        filehandle.close()
        ref_hit = Hit.new_from_dict({'x':1., 'y':2000., 'z':30., 'energy':4.,
                                      'pid':-13, 'charge':1.,
                                      'mass':common.pdg_pid_to_mass[13]}, 'pz')
        filehandle = open(tmp_name(), 'r')
        fac = UserHitFactory(format_list, format_units_dict, filehandle, 'pz')
        test_hit = fac.make_hit()
        self.assertEqual(test_hit, ref_hit)
        test_hit = fac.make_hit()
        self.assertEqual(test_hit, ref_hit)
        self.assertRaises(IOError, fac.make_hit)
        filehandle.close()

    def test_bad_format_list(self):
        format_list = ['', 'bad', 'y', 'z', 'energy', 'pid']
        format_units_dict = {'x':'mm', 'y':'m', 'z':'cm', 'energy':'', 'pz':'',
                             'pid':''}
        filehandle = open(tmp_name(), 'w')
        try:
            fac = UserHitFactory(format_list, format_units_dict, filehandle, 'pz')
            self.assertTrue(False, msg="Should have thrown")
        except KeyError:
            pass

    def test_bad_units_list(self):
        format_list = ['', 'x', 'y', 'z', 'energy', 'pid']
        format_units_dict = {'y':'m', 'z':'cm', 'energy':'', 'pz':'',
                             'pid':''}
        filehandle = open(tmp_name(), 'w')
        try:
            fac = UserHitFactory(format_list, format_units_dict, filehandle, 'pz')
            self.assertTrue(False, msg="Should have thrown")
        except KeyError:
            pass
        format_units_dict = {'x':'BAD', 'y':'m', 'z':'cm', 'energy':'', 'pz':'',
                             'pid':''}
        try:
            fac = UserHitFactory(format_list, format_units_dict, filehandle, 'pz')
            self.assertTrue(False, msg="Should have thrown")
        except KeyError:
            pass

if __name__ == "__main__":
    unittest.main()

