"""XPS background calculation (Shirley) and Electron Paramagnetic Resonance (EPR) plotting."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pathlib import Path
from typing import Sequence, Optional
from my_sci_toolkit.viz.style import apply_style, get_figure_dimensions, PALETTES
from my_sci_toolkit.io.export import save_publication_figure
from my_sci_toolkit.registry import tool


def shirley_background(x: np.ndarray, y: np.ndarray, tol: float = 1e-4, max_iter: int = 50) -> np.ndarray:
    """Compute Shirley non-linear inelastic electron scattering background for XPS."""
    n = len(y)
    b = np.zeros(n)
    yl = y[0]
    yr = y[-1]
    
    # Iterative Shirley background calculation
    for _ in range(max_iter):
        cum_int = np.cumsum(y - b)
        total_int = cum_int[-1]
        if total_int == 0:
            break
        b_new = yr + (yl - yr) * (total_int - cum_int) / total_int
        if np.max(np.abs(b_new - b)) < tol:
            b = b_new
            break
        b = b_new
    return b


@tool(
    name="plot_epr_spectrum",
    description="Plot continuous-wave Electron Paramagnetic Resonance (EPR) spectrum.",
    tags=["spectro", "epr"]
)
def plot_epr_spectrum(
    magnetic_field_gauss: Sequence[float],
    first_derivative_signal: Sequence[float],
    sample_name: str = "Sample",
    save_path: Optional[str | Path] = None,
) -> Figure:
    """Plot standard 1st derivative EPR signal."""
    apply_style()
    fig_w, fig_h = get_figure_dimensions("single", 0.65)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)

    ax.plot(magnetic_field_gauss, first_derivative_signal, color=PALETTES["nature"][0], linewidth=1.1, label=sample_name)
    ax.set_xlabel("Magnetic Field (Gauss)")
    ax.set_ylabel("dI / dB (a.u.)")
    ax.axhline(0, color='grey', linestyle=':', linewidth=0.6)
    ax.legend()

    if save_path:
        save_publication_figure(fig, save_path)
    return fig
