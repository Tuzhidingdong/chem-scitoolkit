"""Cyclic voltammetry (CV) and electrochemical impedance spectroscopy (EIS) visualization."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
from typing import Sequence, Optional
from my_sci_toolkit.viz.style import apply_style, get_figure_dimensions, PALETTES
from my_sci_toolkit.io.export import save_publication_figure
from my_sci_toolkit.registry import tool


@tool(
    name="plot_cv_curve",
    description="Plot cyclic voltammetry (CV) curves (Current vs Potential).",
    tags=["electrochem"]
)
def plot_cv_curve(
    potential_v: Sequence[float],
    current_ma: Sequence[float],
    scan_rate_mv_s: Optional[float] = None,
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot cyclic voltammogram with publication standards."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 0.80)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    lbl = f"{scan_rate_mv_s} mV s$^{{-1}}$" if scan_rate_mv_s else "CV"
    ax.plot(potential_v, current_ma, color=PALETTES["nature"][0], linewidth=1.2, label=lbl)
    ax.set_xlabel("Potential (V)")
    ax.set_ylabel("Current (mA)")
    ax.axhline(0, color='grey', linestyle=':', linewidth=0.6)
    ax.legend()

    if save_path:
        save_publication_figure(fig, save_path)
    return fig


@tool(
    name="plot_nyquist_eis",
    description="Plot electrochemical impedance spectroscopy (EIS) Nyquist plot (-Z'' vs Z').",
    tags=["electrochem"]
)
def plot_nyquist_eis(
    z_real_ohm: Sequence[float],
    z_imag_ohm: Sequence[float],
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot standard Nyquist representation with equal aspect ratio."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 1.0)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    # -Z'' vs Z'
    z_imag_neg = -np.asarray(z_imag_ohm, dtype=float)
    ax.scatter(z_real_ohm, z_imag_neg, color=PALETTES["nature"][0], s=14, facecolors='none', edgecolors=PALETTES["nature"][0])
    ax.set_xlabel(r"Z$'$ ($\Omega$)")
    ax.set_ylabel(r"-Z$''$ ($\Omega$)")
    ax.set_aspect("equal", adjustable="datalim")

    if save_path:
        save_publication_figure(fig, save_path)
    return fig
