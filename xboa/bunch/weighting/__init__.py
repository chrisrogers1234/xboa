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
\namespace xboa::bunch::weighting

The weighting module provides algorithms for performing statistical weighting of
bunches. 

Implemented within this module:
\li \link xboa::bunch::weighting::_voronoi_weighting::VoronoiWeighting
    VoronoiWeighting \endlink: class to apply weights based on a Voronoi
    tesselation.
\li \link xboa::bunch::weighting::_bounding_ellipse::BoundingEllipse
    BoundingEllipse \endlink: defines a BoundingEllipse for the VoronoiWeighting
\li \link xboa::bunch::weighting::_hull_content::HullContent
    HullContent \endlink: is used for parallelised calculation of the contents
    of convex hulls (voronoi tiles). 
"""

from xboa.bunch.weighting._voronoi_weighting import VoronoiWeighting
from xboa.bunch.weighting._bounding_ellipse import BoundingEllipse
from xboa.bunch.weighting._hull_content import HullContent
from xboa.bunch.weighting._multipole_weighting import MultipoleWeighting

__all__ = ["VoronoiWeighting", "BoundingEllipse", "HullContent"]
