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

import unittest

import numpy

from xboa.tracking import TimeoutTracking
from xboa.hit import Hit
from xboa.tracking import MultiTrack
from xboa.tracking.tracking_process import ThisNodeProcess

class MultiTrackTest(unittest.TestCase):
    def setUp(self):
        offset_in = numpy.matrix(numpy.zeros([1, 6]))
        offset_out = [numpy.matrix(numpy.zeros([1, 6]))]
        matrices = [numpy.matrix(numpy.zeros([6, 6]))]
        for i in range(6):
            matrices[0][i, i] = i
        self.tracking = TimeoutTracking(matrices, offset_out, offset_in, 0)
        self.hit_list = [Hit.new_from_dict({'x':i}) for i in range(1000)]

    def test_init(self):
        test_multi = MultiTrack(3, ThisNodeProcess(self.tracking))

    def test_track_many_async(self):
        ref_out = self.tracking.track_many(self.hit_list)
        self.tracking.timeout = 1
        test_multi = MultiTrack(3, ThisNodeProcess(self.tracking))
        test_multi.track_many_async(self.hit_list)
        self.assertLess(len(test_multi.get_return_value()), len(self.hit_list))
        self.assertEqual(len(test_multi.job_list), 3)
        for job, ref_length in zip(test_multi.job_list, [334, 333, 333]):
            self.assertEqual(len(job.hit_list), ref_length)
        while len(test_multi.get_return_value()) < len(self.hit_list):
            pass
        test_out = test_multi.last
        self.assertEqual(len(ref_out), len(test_out))
        for ref_hit_list, test_hit_list in zip(ref_out, test_out):
            self.assertEqual(len(ref_hit_list), len(test_hit_list))
            for ref_hit, test_hit in zip(ref_hit_list, test_hit_list):
                self.assertEqual(ref_hit, test_hit)

    def test_track_many(self):
        test_multi = MultiTrack(3, ThisNodeProcess(self.tracking))
        test_out = test_multi.track_many(self.hit_list)
        self.assertEqual(len(test_out), len(self.hit_list))


if __name__ == "__main__":
    unittest.main()
