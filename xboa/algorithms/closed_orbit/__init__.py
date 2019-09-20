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
\namespace xboa::algorithms::closed_orbit

The closed_orbit module provides algorithms for finding closed_orbits

Implemented within this module:
\li \link xboa::algorithms::closed_orbit::_ellipse_closed_orbit_finder::EllipseClosedOrbitFinder EllipseClosedOrbitFinder \endlink: 
  class for finding closed orbits based on fitting a beam ellipse to a set of 
  input tracking data.
\li \link xboa::algorithms::closed_orbit::_ellipse_closed_orbit_finder::EllipseClosedOrbitFinderIteration EllipseClosedOrbitFinderIteration \endlink:
  helper class for EllipseClosedOrbitFinder; this class represents the output of
  a single iteration of the closed orbit finder
"""

from _ellipse_closed_orbit_finder import EllipseClosedOrbitFinder
from _ellipse_closed_orbit_finder import EllipseClosedOrbitFinderIteration

__all__ = ["EllipseClosedOrbitFinder", "EllipseClosedOrbitFinderIteration"]

