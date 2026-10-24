"""Spectroscopy analysis and plotting module (XRD, FTIR, Raman, XPS, EPR)."""

from my_sci_toolkit.spectro.xrd import (
    plot_xrd_pattern,
    plot_xrd_stack,
)
from my_sci_toolkit.spectro.vibrational import (
    plot_vibrational_spectrum,
    deconvolute_peaks,
)
from my_sci_toolkit.spectro.xps_epr import (
    shirley_background,
    plot_epr_spectrum,
)

__all__ = [
    "plot_xrd_pattern",
    "plot_xrd_stack",
    "plot_vibrational_spectrum",
    "deconvolute_peaks",
    "shirley_background",
    "plot_epr_spectrum",
]
