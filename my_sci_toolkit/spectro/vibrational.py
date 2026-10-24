"""Infrared (FTIR) and Raman vibrational spectroscopy, peak deconvolutions."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
from typing import Sequence, Optional, List, Tuple
from scipy.optimize import curve_fit
from my_sci_toolkit.core.signal import baseline_correct, normalize_minmax
from my_sci_toolkit.viz.style import apply_style, get_figure_dimensions, PALETTES
from my_sci_toolkit.io.export import save_publication_figure
from my_sci_toolkit.registry import tool


def gaussian(x: np.ndarray, amp: float, cen: float, wid: float) -> np.ndarray:
    """Standard Gaussian peak profile."""
    return amp * np.exp(-((x - cen) ** 2) / (2 * (wid ** 2)))


@tool(
    name="plot_vibrational_spectrum",
    description="Plot FTIR or Raman spectrum with optional baseline correction and spectral window trimming.",
    tags=["spectro", "raman", "ir"]
)
def plot_vibrational_spectrum(
    wavenumber: Sequence[float],
    intensity: Sequence[float],
    spec_type: str = "FTIR",
    trim_range: Optional[Tuple[float, float]] = None,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot publication-grade vibrational spectrum."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 0.75)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    x = np.asarray(wavenumber, dtype=float)
    y = np.asarray(intensity, dtype=float)

    if trim_range:
        mask = (x >= trim_range[0]) & (x <= trim_range[1])
        x, y = x[mask], y[mask]

    y_corr = normalize_minmax(baseline_correct(y))

    ax.plot(x, y_corr, color=PALETTES["nature"][0], linewidth=1.1)
    x_lbl = r"Wavenumber (cm$^{-1}$)"
    ax.set_xlabel(x_lbl)
    ax.set_ylabel("Absorbance (a.u.)" if spec_type.upper() == "FTIR" else "Raman Intensity (a.u.)")
    if spec_type.upper() == "FTIR":
        ax.invert_xaxis()  # Conventional FTIR representation

    if save_path:
        save_publication_figure(fig, save_path)
    return fig


@tool(
    name="deconvolute_peaks",
    description="Deconvolute overlapping spectroscopic bands into multiple Gaussian sub-peaks.",
    tags=["spectro", "fitting"]
)
def deconvolute_peaks(
    x: Sequence[float],
    y: Sequence[float],
    initial_centers: Sequence[float],
    initial_widths: Optional[Sequence[float]] = None,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Fit overlapping peaks with multiple Gaussian components and plot deconvolution."""
    apply_style()
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    n_peaks = len(initial_centers)
    widths = initial_widths if initial_widths else [15.0] * n_peaks

    # Initial parameter vector [amp1, cen1, wid1, amp2, cen2, wid2, ...]
    p0: List[float] = []
    for cen, wid in zip(initial_centers, widths):
        p0.extend([np.max(y_arr) * 0.8, cen, wid])

    def multi_gaussian(x_val, *params):
        total = np.zeros_like(x_val)
        for i in range(0, len(params), 3):
            total += gaussian(x_val, params[i], params[i + 1], params[i + 2])
        return total

    popt, _ = curve_fit(multi_gaussian, x_arr, y_arr, p0=p0, maxfev=10000)

    fig_w, fig_h = get_figure_dimensions("single", 0.80)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    ax.scatter(x_arr, y_arr, color='black', s=10, label="Experimental", zorder=3)
    ax.plot(x_arr, multi_gaussian(x_arr, *popt), color='red', linestyle='--', linewidth=1.2, label="Cumulative Fit", zorder=4)

    colors = PALETTES["nature"]
    for i in range(0, len(popt), 3):
        comp = gaussian(x_arr, popt[i], popt[i + 1], popt[i + 2])
        ax.fill_between(x_arr, 0, comp, color=colors[(i // 3) % len(colors)], alpha=0.35, label=f"Peak {popt[i+1]:.1f}")

    ax.set_xlabel(r"Wavenumber (cm$^{-1}$)")
    ax.set_ylabel("Intensity")
    ax.legend()

    if save_path:
        save_publication_figure(fig, save_path)
    return fig
