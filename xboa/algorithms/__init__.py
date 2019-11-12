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
\namespace xboa::algorithms

The algorithms module provides algorithms for performing common accelerator
physics tasks

Implemented within this module:
\li \link xboa::algorithms::closed_orbit closed_orbit \endlink: module 
    containing closed orbit finding routines.
\li \link xboa::algorithms::tune tune \endlink: module containing tune finding 
    routines.
\li \link xboa::algorithms::smoothing smoothing \endlink: module containing 
    smoothing routines (for removing noise from noisy signals).
\li \link xboa::algorithms::peak_finder peak_finder \endlink: module containing 
    peak finding routines.
"""

try:
    import xboa.algorithms.closed_orbit as closed_orbit
except ImportError:
    pass
try:
    import xboa.algorithms.tune as tune
except ImportError:
    pass
try:
    import xboa.algorithms.peak_finder as peak_finder
except ImportError:
    pass
try:
    import xboa.algorithms.smoothing as smoothing
except ImportError:
    pass

__all__ = ["closed_orbit", "tune", "smoothing", "peak_finder"]

