"""
\namespace xboa::algorithms::peak_finder

Algorithms to find peaks in potentially noisy data.

Implemented within this module:
\li \link xboa::algorithms::peak_finder::_window_peak_finder::WindowPeakFinder WindowPeakFinder \endlink: 
    Find peaks by searching for highest point in a window, stepping through the
    data set.
\li \link xboa::algorithms::peak_finder::_uphill_downhill_peak_finder::UphillDownhillPeakFinder UphillDownhillPeakFinder \endlink: 
    Find peaks by looking for a change in first derivative in the data.
\li \link xboa::algorithms::peak_finder::_refine_peak_finder::RefinePeakFinder RefinePeakFinder \endlink: 
    Find peaks by attempting to fit a quadrative to data, given a likely
    position for the peaks as a seed.
"""

from _window_peak_finder import WindowPeakFinder
from _uphill_downhill_peak_finder import UphillDownhillPeakFinder
from _refine_peak_finder import RefinePeakFinder

__all__ = ["WindowPeakFinder", "UphillDownhillPeakFinder", "RefinePeakFinder"]


