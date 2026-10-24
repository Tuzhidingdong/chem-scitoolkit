"""X-ray Diffraction (XRD) plotting, stacking, and in-situ 2D colormaps."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
from typing import Sequence, List, Optional, Tuple
from my_sci_toolkit.core.signal import normalize_minmax, baseline_correct
from my_sci_toolkit.viz.style import apply_style, get_figure_dimensions, PALETTES
from my_sci_toolkit.io.export import save_publication_figure
from my_sci_toolkit.registry import tool


@tool(
    name="plot_xrd_pattern",
    description="Plot standard 1D XRD pattern (Intensity vs 2-Theta).",
    tags=["spectro", "xrd"]
)
def plot_xrd_pattern(
    two_theta: Sequence[float],
    intensity: Sequence[float],
    label: str = "Sample",
    baseline_corr: bool = True,
    normalize: bool = True,
    color: Optional[str] = None,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot publication-grade XRD spectrum."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 0.70)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    y = np.asarray(intensity, dtype=float)
    if baseline_corr:
        y = baseline_correct(y)
    if normalize:
        y = normalize_minmax(y)

    c = color or PALETTES["nature"][0]
    ax.plot(two_theta, y, color=c, linewidth=1.0, label=label)
    ax.set_xlabel(r"2$\theta$ (degree)")
    ax.set_ylabel("Intensity (a.u.)")
    ax.set_yticks([])
    ax.legend()

    if save_path:
        save_publication_figure(fig, save_path)
    return fig


@tool(
    name="plot_xrd_stack",
    description="Plot stacked XRD patterns with vertical offsets (e.g. tracking phase evolution over time or composition).",
    tags=["spectro", "xrd"]
)
def plot_xrd_stack(
    two_theta: Sequence[float],
    intensity_series: Sequence[Sequence[float]],
    labels: Sequence[str],
    offset: float = 0.35,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Stack multiple XRD profiles vertically with controlled baseline separation."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 1.10)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    colors = PALETTES["nature"]
    for idx, (inten, lbl) in enumerate(zip(intensity_series, labels)):
        y_norm = normalize_minmax(baseline_correct(inten))
        y_shifted = y_norm + idx * offset
        col = colors[idx % len(colors)]
        ax.plot(two_theta, y_shifted, color=col, linewidth=0.9, label=lbl)

    ax.set_xlabel(r"2$\theta$ (degree)")
    ax.set_ylabel("Intensity (a.u.)")
    ax.set_yticks([])
    ax.legend(loc="upper right")

    if save_path:
        save_publication_figure(fig, save_path)
    return fig
