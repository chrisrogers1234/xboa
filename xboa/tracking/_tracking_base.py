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
\namespace xboa::tracking::_tracking_base

Should be imported directly from the xboa::tracking namespace
"""

class TrackingBase(object):
    """
    Base class provides an interface to particle tracking routines for use by
    xboa.algorithms
    - last: list of list of hits corresponding to hits from the most recent call
      to track_one or track_many; if last call was to track_one, then last will
      be of length 1
    """
    def __init__(self):
        self.last = []

    def track_one(self, hit):
        """
        Track a hit and return a list of output hits
        - hit initial particle coordinates to be tracked

        Track a hit and return a list of output hits. The output hits should
        corresponds to e.g. particle crossings over cell ends, depending on the
        usage of the Tracking object. The first item in the list should be the
        input hit.
        """
        raise NotImplementedError("track_one was not implemented")

    def track_many(self, list_of_hits):
        """
        Track many hits and return a list of list of output hits
        - list_of_hits list of initial particle corodinates to be tracked

        Track many hits and return a list containing a list of output hits,
        one for each track. This provides a hook for tracking codes that have
        significant set up and tear down times, or which simulate collective
        effects that need to be taken into account by the algorithm

        By default this calls track_one for each hit; but can be overloaded by
        a base class
        """
        hits_out = [self.track_one(hit) for hit in list_of_hits]
        self.last = hits_out
        return hits_out

    

