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
\namespace xboa::tracking::_timeout_tracking

Should be imported directly from the xboa::tracking namespace
"""


import time
from xboa.tracking import MatrixTracking

class TimeoutTracking(MatrixTracking):
    """
    Wrap MatrixTracking with an additional timeout parameter - for testing
    """
    def __init__(self, list_of_transfer_matrices, list_of_offsets, offset_in,
                 timeout):
        """
        As per matrix tracking but with additional timeout parameter
        - timeout: causes track_many to pause for timeout seconds before return
        """
        MatrixTracking.__init__(self,
                                list_of_transfer_matrices,
                                list_of_offsets,
                                offset_in)
        self.timeout = timeout

    def track_many(self, hit_list):
        """Track the hits through the matrices"""
        tracking_out = MatrixTracking.track_many(self, hit_list)
        time.sleep(self.timeout)
        return tracking_out

