"""
\namespace xboa::algorithms::smoothing

Algorithms to clean up noisy data by averaging over nearby points.

Implemented within this module:
\li \link xboa::algorithms::smoothing::_gaussian_smoothing::GaussianSmoothing GaussianSmoothing \endlink: 
    Smooth by summing nearby points, using a Gaussian function to weight the
    relative contributions.
\li \link xboa::algorithms::smoothing::_fit_smoothing::FitSmoothing FitSmoothing \endlink: 
    Smooth by making a piecewise fit to nearby points.
"""


from ._gaussian_smoothing import GaussianSmoothing
from ._fit_smoothing import FitSmoothing
from ._cut_smoothing import CutSmoothing

__all__ = ["GaussianSmoothing", "FitSmoothing", "CutSmoothing"]
