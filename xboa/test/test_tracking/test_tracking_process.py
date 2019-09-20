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

import time
import unittest
import subprocess

import numpy

from xboa.hit import Hit
from xboa.tracking import TimeoutTracking
from xboa.tracking.tracking_process import ThisNodeProcess
from xboa.tracking.tracking_process import BSubProcess

class TrackingProcessBaseTest(unittest.TestCase):
    def setUp(self):
        self.skipTest("Can't run tests on the base class")
        self.time_constant = 10

    def test_init(self):
        process = self.tracking_process
        process.set_hit_list([])
        self.assertFalse(process.is_alive())

        try:
            process.terminate()
            raise ValueError("Should have thrown")
        except RuntimeError:
            pass

        try:
            process.kill()
            raise ValueError("Should have thrown")
        except RuntimeError:
            pass

    def test_pickle_unpickle(self):
        ref_process = self.tracking_process
        ref_process.set_hit_list(self.hit_list)
        ref_out = ref_process.run()
        test_process = ref_process.new_from_pickle(ref_process.out_dir)
        test_out = test_process.run()
        self.assertEqual(len(ref_out), len(test_out))
        for ref_hit, test_hit in zip(ref_out, test_out):
            self.assertEqual(ref_hit, test_hit)

    def test_start(self):
        process = self.tracking_process
        process.set_hit_list(self.hit_list)
        ref_out = process.run()
        process.start()
        process.join()
        self.assertFalse(process.is_alive())
        test_out = process.get_return_value()
        self.assertEqual(len(ref_out), len(test_out))
        for ref_hit, test_hit in zip(ref_out, test_out):
            self.assertEqual(ref_hit, test_hit)
        self.tracking.timeout = 10
        process.start()
        try:
            process.start()
            raise ValueError("start() while running didnt raise exception")
        except RuntimeError:
            pass
        process.kill()

    def test_join(self):
        # note 1 second tolerance for job start and stop
        self.tracking.timeout = 3
        process = self.tracking_process
        process.set_hit_list(self.hit_list)
        process.start()
        start = time.time()

        # timeout < job_time
        process.join(timeout = 1)
        delta_time = time.time() - start
        self.assertGreater(delta_time, 0.5) # should come back after 1 seconds
        self.assertLess(delta_time, 1.5) # should come back after 1 seconds

        # no timeout; should come back after ~ 3 seconds, but process set up and
        # tear down I guess can make things slower
        process.join()
        delta_time = time.time() - start
        self.assertGreater(delta_time, 2.) # should come back after ~ 3 seconds
        self.assertLess(delta_time, 3.+self.time_constant) # should come back after ~ 3 seconds

        # timeout > job_time
        start = time.time()
        process.start()
        process.join(100)
        delta_time = time.time() - start
        self.assertLess(delta_time, 3.+self.time_constant) # should come back after ~ 3 seconds

    def test_is_alive(self):
        self.tracking.timeout = 3
        process = self.tracking_process
        process.set_hit_list(self.hit_list)
        self.assertFalse(process.is_alive())
        process.start()
        self.assertTrue(process.is_alive())
        process.join()
        self.assertFalse(process.is_alive())
        
    def test_terminate_kill(self):
        self.tracking.timeout = 100
        process = self.tracking_process
        process.set_hit_list(self.hit_list)
        try:
            process.terminate()
            raise ValueError("terminate() before start() didnt raise exception")
        except RuntimeError:
            pass
        try:
            process.kill()
            raise ValueError("kill() before start() should raise exception")
        except RuntimeError:
            pass
        self.assertEqual(process.exitcode, None)
        self.assertFalse(process.is_alive())
        process.start()
        self.assertTrue(process.is_alive())
        process.terminate(10)
        self.assertFalse(process.is_alive())
        self.assertEqual(type(process.exitcode), int)
        process.start()
        self.assertTrue(process.is_alive())
        process.exitcode = None
        process.kill(10)
        self.assertFalse(process.is_alive())
        self.assertEqual(type(process.exitcode), int)

    def test_get_return_value(self):
        process = self.tracking_process
        process.set_hit_list(self.hit_list)
        try:
            process.get_return_value()
            raise ValueError("get_return_value() before start should raise exc")
        except RuntimeError:
            pass
        process.start()
        process.join()
        test_out = process.get_return_value()
        ref_out = process.run()
        self.assertEqual(len(test_out), len(ref_out))
        for test_hit, ref_hit in zip(test_out, ref_out):
            self.assertEqual(test_hit, ref_hit)

    tracking_process = None

class ThisNodeTest(TrackingProcessBaseTest):
    @classmethod
    def setUpClass(self):
        pass

    def setUp(self):
        offset_in = numpy.matrix(numpy.zeros([1, 6]))
        offset_out = [numpy.matrix(numpy.zeros([1, 6]))]
        matrices = [numpy.matrix(numpy.zeros([6, 6]))]
        for i in range(6):
            matrices[0][i, i] = i
        self.tracking = TimeoutTracking(matrices, offset_out, offset_in, 0)
        self.hit_list = [Hit.new_from_dict({'x':1, 'y':2})]
        self.tracking_process = ThisNodeProcess(self.tracking)
        self.time_constant = 10

class BSubTest(TrackingProcessBaseTest):
    def setUp(self):
        if not BSubProcess.has_bsub():
            self.skipTest("Require bsub to run this test")
        offset_in = numpy.matrix(numpy.zeros([1, 6]))
        offset_out = [numpy.matrix(numpy.zeros([1, 6]))]
        matrices = [numpy.matrix(numpy.zeros([6, 6]))]
        for i in range(6):
            matrices[0][i, i] = i
        self.tracking = TimeoutTracking(matrices, offset_out, offset_in, 0)
        self.hit_list = [Hit.new_from_dict({'x':1, 'y':2})]
        self.time_constant = 20
        self.tracking_process = BSubProcess(self.tracking, 'scarf-ibis', '00:30')


if __name__ == "__main__":
    unittest.main()


