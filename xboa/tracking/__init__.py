# This file is a part of xboa
#
# xboa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,  or
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

"""
\namespace xboa::tracking

The tracking module holds classes related to tracking interfaces for various
Monte Carlo codes. The tracking interface enables the user to implement basic
tracking for using xboa algorithms against different codes.

Implemented within this module:
\li \link xboa::tracking::_tracking_base::TrackingBase TrackingBase \endlink: base class that defines an interface suitable for use within the
                tracking module
\li \link xboa::tracking::_maus_tracking::MAUSTracking MAUSTracking \endlink: a tracking class that provides an interface to the MAUS tracking
                library
\li \link xboa::tracking::_matrix_tracking::MatrixTracking MatrixTracking \endlink: a tracking class that provides an interface to "tracking"
                using simple transfer matrices
"""

from _matrix_tracking import MatrixTracking
from _maus_tracking import MAUSTracking
from _tracking_base import TrackingBase
from _timeout_tracking import TimeoutTracking
from _multitrack import MultiTrack
import tracking_process

__all__ = ["MatrixTracking",
           "MAUSTracking",
           "TrackingBase",
           "TimeoutTracking",
           "MultiTrack"]

