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
\namespace xboa::algorithms::tune

The tune module provides algorithms for finding the tune

Implemented within this module:
\li \link xboa::algorithms::tune::_fft_tune::FFTTuneFinder FFTTuneFinder \endlink: 
    FFT wrapper routines for getting the tune from a set of positional data.
"""
from ._fft_tune import FFTTuneFinder
from ._dphi_tune import DPhiTuneFinder

__all__ = ["FFTTuneFinder", "DPhiTuneFinder"]
