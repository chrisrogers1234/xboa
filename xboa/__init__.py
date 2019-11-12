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

"""
\namespace xboa

XBOA - Cross-Platform Beam Optics Analysis
A multiparticle tracking postprocessor library for accelerator physicists.

You\'ve got your favourite tracking code running, what now? This package is a 
post-processor for taking beam data to calculate emittance, Twiss functions,
etc. Also includes bindings to plotting packages ROOT and matplotlib, and a 
whole lot more!

"""

__version__ = '0.17.0'
__all__ = ['bunch', 'hit', 'common', 'tracking', 'algorithms']

