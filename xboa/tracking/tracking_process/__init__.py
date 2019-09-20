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
\namespace xboa::tracking::tracking_process

The tracking_process module holds classes related to pushing tracking into a
subprocess, in order to support the MultiTrack class.


Implemented within this module:
\li \link xboa::tracking::tracking_process::_tracking_process::TrackingProcess TrackingProcess \endlink: base class that defines an interface suitable for distributing tracking
\li \link xboa::tracking::tracking_process::_this_node_process::ThisNodeProcess ThisNodeProcess\endlink: uses the subprocess module to run subprocesses on this node
"""
from _tracking_process import TrackingProcess
from _this_node_process import ThisNodeProcess
from _bsub_process import BSubProcess

__all__ = ["TrackingProcess", "ThisNodeProcess", "BSubProcess"]


